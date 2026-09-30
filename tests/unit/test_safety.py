import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from safety_checks import preflight_test, preflight, static_checks

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

launcher = load("launcher", ROOT / "services/terraform-mcp/launch.py")
renderer = load("renderer", ROOT / "scripts/render-registry-root.py")

class SafetyTests(unittest.TestCase):
    def test_preflight_accepts_only_reviewed_mock_plans(self):
        self.assertEqual(preflight(ROOT), 10)
        static_checks(ROOT)
    def test_preflight_rejects_implicit_apply_and_real_override(self):
        bad = [
            'mock_provider "aws" {}\nrun "bad" {}',
            'mock_provider "aws" {}\nrun "bad" { command = apply }',
            'provider "aws" {}\nrun "bad" { command = plan }',
            'mock_provider "aws" {}\nrun "bad" { command = plan providers = { aws = aws.real } }',
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.tftest.hcl"
            for text in bad:
                path.write_text(text)
                with self.assertRaises(ValueError):
                    preflight_test(path)
    def test_launcher_has_no_token_value_or_docker_socket_or_http(self):
        config = json.loads((ROOT / "services/terraform-mcp/config.json").read_text())
        command = launcher.build_command(config)
        self.assertIn("TFE_TOKEN", command)
        self.assertFalse(any(s.startswith("TFE_TOKEN=") for s in command))
        for denied in ["-t", "-p", "--privileged", "--network=host", "/var/run/docker.sock"]:
            self.assertNotIn(denied, command)
        self.assertIn("--read-only", command)
        self.assertIn("--cap-drop=ALL", command)
        self.assertIn("stdio", command)
        self.assertNotIn("streamable-http", command)
    def test_launcher_fails_closed_on_unapproved_config(self):
        config = json.loads((ROOT / "services/terraform-mcp/config.json").read_text())
        config["tools"].append("create_workspace")
        with self.assertRaises(ValueError):
            launcher.build_command(config)
    def test_token_permissions_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "token"
            value = "unit-fixture-opaque-value"
            path.write_text(value)
            path.chmod(0o600)
            self.assertEqual(launcher.read_token(path, os.getuid()), value)
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                launcher.read_token(path, os.getuid())
            link = Path(tmp) / "link"
            link.symlink_to(path)
            with self.assertRaises(OSError):
                launcher.read_token(link, os.getuid())
    def test_launcher_argument_error_does_not_pollute_stdout(self):
        result = subprocess.run(["bash", str(ROOT / "services/terraform-mcp/launch.sh"), "bad"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertNotIn("unit-fixture-opaque-value", result.stderr)
    def test_registry_patches_change_only_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "root"
            renderer.render("fixture-org", destination)
            original = (destination / "main.tf").read_text()
            for patch in ["missing-owner.patch", "fix-owner.patch"]:
                subprocess.run(["git", "apply", str(ROOT / "packages/aws-ai-demo/fixtures" / patch)], cwd=destination, check=True)
                if patch == "missing-owner.patch":
                    self.assertNotIn("Owner", (destination / "main.tf").read_text())
            self.assertEqual((destination / "main.tf").read_text(), original)
            self.assertIn('source      = "app.terraform.io/fixture-org/s3-standard/aws"', original)

if __name__ == "__main__":
    unittest.main()
