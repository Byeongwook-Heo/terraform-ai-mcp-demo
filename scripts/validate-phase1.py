#!/usr/bin/env python3
"""Phase 1 전용: 공개 dependency init, 정적 검사, 네트워크 없는 Mock 검사."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path
from safety_checks import ROOTS, preflight, static_checks

ROOT = Path(__file__).resolve().parents[1]
results = []

def result(name, status, detail):
    results.append({"check": name, "status": status, "detail": detail})
    print(f"{status}: {name} — {detail}", flush=True)

def command(name, args, env, cwd=None):
    process = subprocess.run(args, env=env, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    status = "PASS" if process.returncode == 0 else "FAIL"
    result(name, status, "exit=" + str(process.returncode))
    # fresh environment + reviewed local Mock 출력만 저장합니다.
    logs = ROOT / "reports/validation-logs"
    logs.mkdir(parents=True, exist_ok=True)
    (logs / (name.replace("/", "-") + ".txt")).write_text(process.stdout.rstrip() + "\n")
    return process.returncode == 0

def main():
    with tempfile.TemporaryDirectory(prefix="phase1-validation-") as temporary:
        temp = Path(temporary)
        (temp / "home").mkdir()
        (temp / "docker").mkdir()
        (temp / "empty.tfrc").write_text("disable_checkpoint = true\n")
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(temp / "home"), "TF_CLI_CONFIG_FILE": str(temp / "empty.tfrc"), "TF_IN_AUTOMATION": "1", "CHECKPOINT_DISABLE": "1", "AWS_EC2_METADATA_DISABLED": "true", "DOCKER_CONFIG": str(temp / "docker"), "PYTHONDONTWRITEBYTECODE": "1"}
        # 공개 다운로드용 인증 없는 proxy만 상속하며 값은 기록하지 않습니다.
        for key in ["HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"]:
            value = os.environ.get(key)
            if value:
                parsed = urllib.parse.urlsplit(value)
                if parsed.username or parsed.password:
                    result("environment", "BLOCKED", "인증 정보가 있는 proxy는 상속하지 않습니다.")
                    return
                env[key] = value
        try:
            count = preflight(ROOT)
            static_checks(ROOT)
            result("safety-preflight", "PASS", f"총 {count}개 run이 mock_provider aws + command=plan입니다.")
        except Exception as error:
            result("safety-preflight", "FAIL", str(error))
            return
        copy = temp / "project"
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", ".terraform", "__pycache__", "reports", "*.tfstate*", "*.auto.tfvars", "terraform.tfvars", "*.tfplan"))
        shell = sorted(str(p) for p in ROOT.rglob("*.sh") if ".terraform" not in p.parts)
        for path in shell:
            command("bash-" + Path(path).stem, ["bash", "-n", path], env)
        for tool in ["terraform", "sentinel", "shellcheck", "docker"]:
            if not shutil.which(tool):
                result(tool + "-availability", "SKIPPED", "도구를 찾을 수 없습니다.")
        if shutil.which("shellcheck"):
            command("shellcheck", ["shellcheck", "--severity=warning", *shell], env)
        command("python-unit", [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests/unit"), "-v"], env)
        if shutil.which("sentinel"):
            command("sentinel-mocks", ["sentinel", "test", "-verbose"], env, copy / "packages/terraform-demo-policies")
        if shutil.which("terraform"):
            command("terraform-fmt", ["terraform", "fmt", "-check", "-recursive", str(copy)], env)
            docker_ok = shutil.which("docker") and subprocess.run(["docker", "info"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            if docker_ok:
                docker_ok = command("terraform-test-image", ["docker", "pull", "hashicorp/terraform:1.13.5@sha256:6bbb82d575aa7bd4f0a2c6e3a0838ab9590426c08a71d7a2783643f01004d356"], env)
            for directory in ROOTS:
                label = directory.replace("/", "-")
                if not command("init-" + label, ["terraform", "-chdir=" + str(copy / directory), "init", "-backend=false", "-input=false", "-no-color"], env):
                    result("validate-test-" + label, "BLOCKED", "init이 실패했습니다.")
                    continue
                command("validate-" + label, ["terraform", "-chdir=" + str(copy / directory), "validate", "-no-color"], env)
                if docker_ok:
                    # 격리된 복사본만 mount하며 AWS/HCP 환경변수나 호스트 Docker socket을 전달하지 않습니다.
                    command("mock-plan-" + label, ["docker", "run", "--rm", "--user=" + str(os.getuid()) + ":" + str(os.getgid()), "--network=none", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--mount", f"type=bind,src={temp},dst={temp}", "--entrypoint=terraform", "hashicorp/terraform:1.13.5@sha256:6bbb82d575aa7bd4f0a2c6e3a0838ab9590426c08a71d7a2783643f01004d356", "-chdir=" + str(copy / directory), "test", "-no-color"], env)
                else:
                    result("mock-plan-" + label, "BLOCKED", "network=none Docker를 사용할 수 없습니다.")
        if shutil.which("docker"):
            config = json.loads((ROOT / "services/terraform-mcp/config.json").read_text())
            if not command("mcp-image", ["docker", "pull", config["image"]], env):
                result("mcp-offline-protocol", "BLOCKED", "고정 Image를 가져오지 못했습니다.")
                return
            command("mcp-offline-protocol", [sys.executable, str(ROOT / "tests/mcp/probe.py"), "--offline"], env)

if __name__ == "__main__":
    try:
        main()
    finally:
        (ROOT / "reports/validation-results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    sys.exit(1 if any(r["status"] == "FAIL" for r in results) else 2 if any(r["status"] in ["BLOCKED", "SKIPPED"] for r in results) else 0)
