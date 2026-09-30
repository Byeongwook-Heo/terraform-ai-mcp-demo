import hashlib
import json
import stat
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from demo_preparation import prepare
from publication_verification import verify_prepared


class PublicationVerificationTests(unittest.TestCase):
    def alter_archive(self, output, name=None, content=b"fixture", mode=None):
        path = output / "terraform-aws-s3-standard.zip"
        with zipfile.ZipFile(path, "a") as archive, warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            info = zipfile.ZipInfo(name or "tests/unexpected.tftest.hcl")
            info.external_attr = (mode or (stat.S_IFREG | 0o644)) << 16
            archive.writestr(info, content)
        sums = json.loads((output / "checksums.json").read_text())
        sums[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        (output / "checksums.json").write_text(json.dumps(sums))

    def test_accepts_generated_archives_and_keeps_pending_inputs_distinct(self):
        for config in ({}, {"hcp_organization": "fixture-org", "owner": "fixture-team"}):
            with self.subTest(configured=bool(config)), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "prepared"
                prepare(config, output)
                result = verify_prepared(output)
                self.assertEqual(len(result["checks"]), 3)
                self.assertTrue(all(check["status"] == "PASS" for check in result["checks"]))
                self.assertGreater(result["pending_input_checks"], 0)
                self.assertFalse(result["actual_registry_verified"])
                self.assertFalse(result["aws_hcp_deployed"])

    def test_rejects_missing_archive_wrong_hash_and_unknown_manifest_entry(self):
        for case in ("missing", "hash", "manifest"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "prepared"
                prepare({}, output)
                path = output / "terraform-aws-s3-standard.zip"
                if case == "missing":
                    path.unlink()
                elif case == "hash":
                    path.write_bytes(path.read_bytes() + b"modified")
                else:
                    sums = json.loads((output / "checksums.json").read_text())
                    sums["../untrusted.zip"] = "0" * 64
                    (output / "checksums.json").write_text(json.dumps(sums))
                with self.assertRaises(ValueError):
                    verify_prepared(output)

    def test_rejects_unsafe_zip_members_even_with_updated_checksum(self):
        for name, mode in [("../escape.tf", None), ("/absolute.tf", None),
                           ("tests/../escape.tftest.hcl", None), ("terraform.tfstate", None),
                           ("main.tf", None), ("tests/link.tftest.hcl", stat.S_IFLNK | 0o777)]:
            with self.subTest(kind=name), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "prepared"
                prepare({}, output)
                self.alter_archive(output, name, mode=mode)
                with self.assertRaises(ValueError):
                    verify_prepared(output)

    def test_rejects_secret_content_and_non_boolean_external_status(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "prepared"
            prepare({}, output)
            self.alter_archive(output, content=("# gh" + "p_" + "a" * 32).encode())
            with self.assertRaises(ValueError):
                verify_prepared(output)
        for status in (True, 0, "false"):
            with self.subTest(external_changes=status), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "prepared"
                prepare({}, output)
                path = output / "readiness.json"
                readiness = json.loads(path.read_text())
                readiness["external_changes"] = status
                path.write_text(json.dumps(readiness))
                with self.assertRaises(ValueError):
                    verify_prepared(output)

    def test_rejects_symlinked_archive_without_reading_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / "prepared"
            prepare({}, output)
            path = output / "terraform-aws-s3-standard.zip"
            moved = directory / "outside.zip"
            path.rename(moved)
            path.symlink_to(moved)
            with self.assertRaises(ValueError):
                verify_prepared(output)


if __name__ == "__main__":
    unittest.main()
