"""생성·다운로드한 게시 ZIP 검사. 압축 해제, 외부 API, Terraform 실행 없음."""
import hashlib
import io
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath

from secret_patterns import possible_secret

PACKAGES = {
    "terraform-aws-s3-standard": {"AGENTS.md", "README.md", "main.tf", "variables.tf", "versions.tf", "outputs.tf", ".terraform.lock.hcl"},
    "terraform-demo-policies": {"AGENTS.md", "README.md", "sentinel.hcl", "require-owner.sentinel"},
    "aws-ai-demo": {"AGENTS.md", "README.md", "templates/main.tf.tmpl", "templates/variables.tf.tmpl", "templates/versions.tf.tmpl", "fixtures/missing-owner.patch", "fixtures/fix-owner.patch"},
}
MAX_BYTES = 10 * 1024 * 1024
MAX_FILES = 256


def read_regular(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("필수 파일이 없거나 일반 파일·크기 조건을 만족하지 않습니다.")
    return path.read_bytes()


def allowed_member(package, name):
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or "\\" in name or ":" in name or any(p in {".", ".."} for p in name.split("/")):
        return False
    if name in PACKAGES[package]:
        return True
    parts = path.parts
    if package == "terraform-aws-s3-standard":
        return len(parts) == 2 and parts[0] == "tests" and parts[1].endswith(".tftest.hcl")
    if package == "terraform-demo-policies":
        return ((len(parts) == 2 and parts[0] == "mocks" and parts[1].endswith(".sentinel"))
                or (len(parts) == 3 and parts[:2] == ("test", "require-owner") and parts[2].endswith(".hcl")))
    return name in {"main.tf", "variables.tf", "versions.tf"}


def verify_archive(data, package):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if not entries or len(entries) > MAX_FILES or len(names) != len(set(names)):
            raise ValueError("ZIP이 비어 있거나 파일 수·중복 이름 조건을 만족하지 않습니다.")
        if sum(entry.file_size for entry in entries) > MAX_BYTES:
            raise ValueError("ZIP의 압축 해제 크기 한도를 초과했습니다.")
        if not PACKAGES[package] <= set(names):
            raise ValueError("ZIP의 필수 게시 파일이 누락됐습니다.")
        for entry in entries:
            mode = stat.S_IFMT(entry.external_attr >> 16)
            if not allowed_member(package, entry.filename) or mode not in {0, stat.S_IFREG} or entry.flag_bits & 1:
                raise ValueError("ZIP에 허용되지 않은 경로·파일 형식·암호화 항목이 있습니다.")
            if possible_secret(archive.read(entry).decode("utf-8")):
                raise ValueError("ZIP 내용에서 Secret 패턴을 발견했습니다. 원문은 출력하지 않습니다.")
        return len(entries)


def verify_prepared(directory):
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("준비 결과의 실제 디렉터리를 지정하세요.")
    sums = json.loads(read_regular(directory / "checksums.json"))
    expected = {name + ".zip" for name in PACKAGES}
    if not isinstance(sums, dict) or set(sums) != expected:
        raise ValueError("checksums.json에는 게시 ZIP 3개만 있어야 합니다.")
    readiness = json.loads(read_regular(directory / "readiness.json"))
    if (not isinstance(readiness, dict) or readiness.get("scope") != "local-preparation-only"
            or readiness.get("external_changes") is not False or not isinstance(readiness.get("checks"), list)):
        raise ValueError("준비 결과의 scope와 외부 변경 여부를 확인하세요.")
    if not readiness["checks"] or any(not isinstance(check, dict) or check.get("status") not in {"PASS", "BLOCKED"} for check in readiness["checks"]):
        raise ValueError("readiness.json 검사 결과 형식이 올바르지 않습니다.")
    checks = []
    for package in PACKAGES:
        name = package + ".zip"
        expected_sum = sums[name]
        if not isinstance(expected_sum, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sum):
            raise ValueError("SHA256 형식이 올바르지 않습니다.")
        data = read_regular(directory / name)
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected_sum:
            raise ValueError("ZIP SHA256이 checksums.json과 다릅니다.")
        try:
            files = verify_archive(data, package)
        except (zipfile.BadZipFile, UnicodeDecodeError, RuntimeError, NotImplementedError) as error:
            raise ValueError("ZIP을 안전하게 읽고 검사할 수 없습니다.") from error
        checks.append({"package": name, "status": "PASS", "files": files, "sha256": actual})
    return {"scope": "offline-publication-verification", "checks": checks,
            "actual_registry_verified": False, "aws_hcp_deployed": False,
            "pending_input_checks": sum(check["status"] == "BLOCKED" for check in readiness["checks"])}
