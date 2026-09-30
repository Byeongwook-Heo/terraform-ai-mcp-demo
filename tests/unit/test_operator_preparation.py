import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from operator_preparation import prepare_operator

INPUT = {
    "aws_account_id": "123456789012", "hcp_organization": "fixture-org",
    "vpc_id": "vpc-0123456789abcdef0", "subnet_id": "subnet-0123456789abcdef0",
    "ami_id": "ami-0123456789abcdef0", "owner": "fixture-team",
    "bucket_name": "fixture-demo-bucket", "create_oidc_provider": True,
}


class OperatorPreparationTests(unittest.TestCase):
    def test_review_has_no_backend_and_state_and_demo_execution_are_separate(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "prepared"
            result = prepare_operator(INPUT, output)
            self.assertFalse(result["external_changes"])
            self.assertFalse(result["review_plan_apply_allowed"])
            settings = json.loads((output / "hcp-state-settings.json").read_text())
            self.assertEqual({s["workspace"] for s in settings}, {"mcp-host-state", "hcp-aws-identity-state"})
            for entry in settings:
                self.assertEqual(entry["execution_mode"], "local")
                self.assertFalse(entry["auto_apply"])
                self.assertFalse(entry["aws_credentials_in_workspace"])
                self.assertFalse(entry["global_remote_state"])
            remote = json.loads((output / "publication/inputs/workspace-settings.json").read_text())
            self.assertEqual(remote["execution_mode"], "remote")
            for name in ("mcp-host", "hcp-aws-identity"):
                review = output / "review" / name
                self.assertFalse((review / "backend.tf").exists())
                for file in review.glob("*.tf"):
                    self.assertNotIn("cloud {", file.read_text())
                    self.assertNotIn('backend "', file.read_text())
                self.assertIn('organization = "fixture-org"', (output / "state-overlays" / name / "backend.tf").read_text())
            self.assertTrue((output / "review/mcp-host/bootstrap.sh").is_file())

    def test_refuses_incomplete_inputs_workspace_collision_and_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "prepared"
            for value in ({}, {**INPUT, "hcp_workspace": "mcp-host-state"}):
                with self.assertRaises(ValueError):
                    prepare_operator(value, output)
                self.assertFalse(output.exists())
            prepare_operator(INPUT, output)
            manifest = (output / "manifest.json").read_bytes()
            with self.assertRaises(ValueError):
                prepare_operator(INPUT, output)
            self.assertEqual((output / "manifest.json").read_bytes(), manifest)

    def test_excludes_unreviewed_state_secret_and_backend_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source"
            for folder in ("infra", "packages"):
                shutil.copytree(ROOT / folder, source / folder)
            host = source / "infra/mcp-host"
            for name in ("terraform.tfstate", ".env", "backend.tf", "unexpected.tf"):
                (host / name).write_text("unreviewed-content")
            output = directory / "prepared"
            prepare_operator(INPUT, output, root=source)
            for name in ("terraform.tfstate", ".env", "backend.tf", "unexpected.tf"):
                self.assertFalse((output / "review/mcp-host" / name).exists())
            file = host / "bootstrap.sh"
            file.unlink()
            file.symlink_to(ROOT / "infra/mcp-host/bootstrap.sh")
            rejected = directory / "rejected"
            with self.assertRaises(ValueError):
                prepare_operator(INPUT, rejected, root=source)
            self.assertFalse(rejected.exists())

    def test_rejects_backend_hidden_in_allowlisted_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source"
            for folder in ("infra", "packages"):
                shutil.copytree(ROOT / folder, source / folder)
            file = source / "infra/mcp-host/versions.tf"
            file.write_text(file.read_text() + '\nterraform { cloud { organization = "fixture-org" } }\n')
            output = directory / "rejected"
            with self.assertRaises(ValueError):
                prepare_operator(INPUT, output, root=source)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
