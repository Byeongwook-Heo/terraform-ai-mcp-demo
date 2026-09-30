import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from demo_preparation import prepare, validate_config

COMPLETE = {
    "aws_account_id": "123456789012", "vpc_id": "vpc-0123456789abcdef0",
    "subnet_id": "subnet-0123456789abcdef0", "ami_id": "ami-0123456789abcdef0",
    "hcp_organization": "fixture-org", "bucket_name": "fixture-demo-bucket", "owner": "fixture-team",
    "existing_oidc_provider_arn": "arn:aws:iam::123456789012:oidc-provider/app.terraform.io",
    "mcp_instance_id": "i-0123456789abcdef0", "ssm_session_prefix": "fixture-user",
}


class PreparationTests(unittest.TestCase):
    def test_unknown_inputs_do_not_block_packages_or_become_deployable(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "prepared"
            result = prepare({}, output)
            self.assertFalse(result["external_changes"])
            self.assertEqual(len(list(output.glob("*.zip"))), 3)
            self.assertFalse((output / "inputs").exists())
            self.assertFalse((output / "packages/aws-ai-demo/main.tf").exists())
            self.assertTrue(any(c["status"] == "BLOCKED" for c in result["checks"]))

    def test_complete_inputs_preserve_exact_identity_and_manual_apply(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "prepared"
            result = prepare(COMPLETE, output)
            self.assertTrue(all(c["status"] == "PASS" for c in result["checks"]))
            self.assertFalse(result["external_changes"])
            workspace = json.loads((output / "inputs/workspace-settings.json").read_text())
            self.assertFalse(workspace["auto_apply"])
            identity = json.loads((output / "inputs/hcp-aws-identity.tfvars.json").read_text())
            self.assertEqual(identity["existing_oidc_provider_arn"], COMPLETE["existing_oidc_provider_arn"])
            self.assertFalse(identity["create_oidc_provider"])
            root = (output / "packages/aws-ai-demo/main.tf").read_text()
            self.assertIn('"app.terraform.io/fixture-org/s3-standard/aws"', root)
            self.assertIn('"fixture-team"', root)
            destination = output / "packages/aws-ai-demo"
            for patch in ["missing-owner.patch", "fix-owner.patch"]:
                subprocess.run(["git", "apply", str(destination / "fixtures" / patch)], cwd=destination, check=True, capture_output=True)
                if patch == "missing-owner.patch":
                    self.assertNotIn("Owner", (destination / "main.tf").read_text())
            self.assertEqual((destination / "main.tf").read_text(), root)
            client = (output / "inputs/iam-ssm-client.json").read_text()
            self.assertNotIn("REPLACE", client)
            self.assertIn("AWS-StartSSHSession", client)
            self.assertIn(COMPLETE["mcp_instance_id"], client)

    def test_rejects_secret_unknown_fields_interpolation_and_wrong_identity(self):
        invalid = [
            {"token": "fixture-secret"}, {"aws_account_id": "000000000000"},
            {"owner": "${unsafe}"}, {"hcp_project": "project:*"},
            {"owner": "gh" + "p_" + "a" * 32}, {"create_oidc_provider": "false"},
            {"schema_version": True}, {"aws_region": "cn-north-1"},
            {**COMPLETE, "existing_oidc_provider_arn": "arn:aws:iam::999999999999:oidc-provider/app.terraform.io"},
            {**COMPLETE, "create_oidc_provider": True},
            {"bucket_name": "192.168.0.1"}, {"bucket_name": "reserved--x-s3"},
        ]
        for value in invalid:
            with self.subTest(fields=sorted(value)), self.assertRaises(ValueError):
                validate_config(value)

    def test_packages_are_repeatable_and_exclude_state_and_unreviewed_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source"
            shutil.copytree(ROOT / "packages", source / "packages")
            package = source / "packages/terraform-aws-s3-standard"
            (package / "terraform.tfstate").write_text("fixture-state")
            (package / ".env").write_text("fixture-value")
            (package / "unexpected.tf").write_text("fixture-file")
            first, second = directory / "one", directory / "two"
            prepare({}, first, root=source)
            prepare({}, second, root=source)
            self.assertEqual((first / "checksums.json").read_bytes(), (second / "checksums.json").read_bytes())
            with zipfile.ZipFile(first / "terraform-aws-s3-standard.zip") as archive:
                self.assertFalse(set(archive.namelist()) & {"terraform.tfstate", ".env", "unexpected.tf"})
                self.assertIn("AGENTS.md", archive.namelist())
            with self.assertRaises(ValueError):
                prepare({}, first, root=source)

    def test_export_refuses_symlinks_and_secret_content_without_partial_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source"
            shutil.copytree(ROOT / "packages", source / "packages")
            file = source / "packages/terraform-aws-s3-standard/main.tf"
            original = file.read_text()
            file.unlink()
            file.symlink_to(ROOT / "packages/terraform-aws-s3-standard/main.tf")
            output = directory / "prepared"
            with self.assertRaises(ValueError):
                prepare({}, output, root=source)
            self.assertFalse(output.exists())
            file.unlink()
            file.write_text(original + '\n# gh' + 'p_' + 'a' * 32 + '\n')
            with self.assertRaises(ValueError):
                prepare({}, output, root=source)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
