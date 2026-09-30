#!/usr/bin/env python3
"""Registry Root patch와 실제 Sentinel CLI의 정상/누락/수정 흐름을 계정 없이 검증."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
import hcl2

ROOT = Path(__file__).resolve().parents[1]


def rehearse():
    spec = importlib.util.spec_from_file_location("renderer", ROOT / "scripts/render-registry-root.py")
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    policy = ROOT / "packages/terraform-demo-policies/require-owner.sentinel"
    policy_bytes = policy.read_bytes()
    rows = []
    with tempfile.TemporaryDirectory(prefix="demo-rehearsal-") as temporary:
        directory = Path(temporary)
        root = directory / "registry-root"
        renderer.render("fixture-org", root)
        original = {p.name: p.read_bytes() for p in root.glob("*.tf")}
        for scenario, patch, expected in [("normal", None, True), ("missing-owner", "missing-owner.patch", False), ("fixed-owner", "fix-owner.patch", True)]:
            if patch:
                subprocess.run(["git", "apply", str(ROOT / "packages/aws-ai-demo/fixtures" / patch)], cwd=root, check=True, capture_output=True)
            body = hcl2.loads((root / "main.tf").read_text())["module"][0]["s3_standard"]
            if body["source"] != "app.terraform.io/fixture-org/s3-standard/aws" or body["version"] != "1.0.0":
                raise ValueError("Registry source/version이 변경됐습니다.")
            tags = body["tags"]
            if tags != ({"Environment": "demo", "Owner": "demo-team"} if expected else {"Environment": "demo"}):
                raise ValueError("Root에서 Owner 외 필드가 변경됐습니다.")
            for name, data in original.items():
                if name != "main.tf" and (root / name).read_bytes() != data:
                    raise ValueError("Root의 다른 파일이 변경됐습니다.")
            changes = {"module.s3_standard.aws_s3_bucket.this": {"type": "aws_s3_bucket", "mode": "managed", "change": {"actions": ["create"], "after": {"tags_all": tags}, "after_unknown": {}}}}
            (directory / "mock.sentinel").write_text("resource_changes = " + json.dumps(changes) + "\n")
            config = directory / "sentinel.hcl"
            config.write_text('mock "tfplan/v2" {\n  module { source = "./mock.sentinel" }\n}\n')
            result = subprocess.run(["sentinel", "apply", "-json-rule=main", "-config=" + str(config), str(policy)], cwd=directory, capture_output=True, text=True, timeout=30)
            if result.returncode != (0 if expected else 1) or json.loads(result.stdout) is not expected:
                raise ValueError("Sentinel의 실제 정책 결과가 시나리오와 일치하지 않습니다.")
            rows.append({"scenario": scenario, "status": "PASS", "policy_result": expected, "sentinel_exit": result.returncode})
        if (root / "main.tf").read_bytes() != original["main.tf"] or policy.read_bytes() != policy_bytes:
            raise ValueError("수정 후 Root 또는 Policy 원본이 일치하지 않습니다.")
    return {"scope": "offline-fixture-rehearsal", "actual_registry": False, "aws_resources_created": False,
            "plan_evidence": "별도 Terraform network=none mock_provider plan 테스트 결과 참조; 실제 tfplan export 아님",
            "policy_sha256": hashlib.sha256(policy_bytes).hexdigest(), "scenarios": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = rehearse()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    for row in result["scenarios"]:
        print(f"PASS: {row['scenario']} — policy={row['policy_result']} (offline fixture)")
