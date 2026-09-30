"""검증 결과 경로의 기존 증거 보존과 잘못된 인수 거부를 확인합니다."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ValidationOutputTests(unittest.TestCase):
    def test_existing_output_is_rejected_without_changing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "validation-results.json"
            evidence.write_text('existing evidence\n')
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate-phase1.py"),
                 "--reports-dir", directory], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(evidence.read_text(), 'existing evidence\n')
            self.assertEqual(list(Path(directory).iterdir()), [evidence])

    def test_live_argument_is_rejected_before_validation(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate-phase1.py"), "--live"],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
