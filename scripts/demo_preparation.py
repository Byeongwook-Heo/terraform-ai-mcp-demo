"""계정 없는 게시 패키지와 비민감 운영 입력 파일 생성. 외부 호출 없음."""
import hashlib
import ipaddress
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from secret_patterns import possible_secret

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "aws_region": r"(?:af|ap|ca|eu|il|me|mx|sa|us)-(?:central|east|north|northeast|northwest|south|southeast|southwest|west)-[1-9]",
    "aws_account_id": r"\d{12}",
    "vpc_id": r"vpc-(?:[0-9a-f]{8}|[0-9a-f]{17})",
    "subnet_id": r"subnet-(?:[0-9a-f]{8}|[0-9a-f]{17})",
    "ami_id": r"ami-(?:[0-9a-f]{8}|[0-9a-f]{17})",
    "mcp_instance_id": r"i-(?:[0-9a-f]{8}|[0-9a-f]{17})",
    "hcp_organization": r"[A-Za-z0-9_-]+",
    "hcp_project": r"[A-Za-z0-9][A-Za-z0-9 _.-]{0,127}",
    "hcp_workspace": r"[A-Za-z0-9_-]+",
    "bucket_name": r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]",
    "owner": r"[A-Za-z0-9][A-Za-z0-9_.@ /-]{0,127}",
    "existing_oidc_provider_arn": r"arn:aws:iam::\d{12}:oidc-provider/app\.terraform\.io",
    "ssm_session_prefix": r"[A-Za-z0-9][A-Za-z0-9_.@-]{0,127}",
}
BOOLS = {"associate_public_ip_address", "create_oidc_provider"}
DEFAULTS = {
    "schema_version": 1, "aws_region": "ap-northeast-2",
    "hcp_project": "mcp-demo", "hcp_workspace": "aws-ai-demo",
    "associate_public_ip_address": False, "create_oidc_provider": False,
}


def validate_config(value):
    if not isinstance(value, dict) or set(value) - (set(PATTERNS) | BOOLS | {"schema_version"}):
        raise ValueError("입력은 허용된 비민감 필드만 포함하는 JSON object여야 합니다.")
    config = {**dict.fromkeys(PATTERNS), **DEFAULTS, **value}
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ValueError("schema_version은 1이어야 합니다.")
    for key in BOOLS:
        if type(config[key]) is not bool:
            raise ValueError(f"{key}는 boolean이어야 합니다.")
    for key, pattern in PATTERNS.items():
        item = config[key]
        if item is None:
            continue
        if not isinstance(item, str) or not re.fullmatch(pattern, item):
            raise ValueError(f"{key} 형식을 확인하세요. 입력값은 출력하지 않습니다.")
        if possible_secret(item):
            raise ValueError("Secret으로 보이는 입력은 허용하지 않습니다.")
        if "REPLACE" in item or item.startswith("replace-") or (key == "aws_account_id" and item == "0" * 12):
            raise ValueError(f"{key}에 placeholder 대신 확인된 값 또는 null을 사용하세요.")
    if any(config[key] is None for key in ("aws_region", "hcp_project", "hcp_workspace")):
        raise ValueError("aws_region/hcp_project/hcp_workspace에는 값이 필요합니다.")
    bucket = config["bucket_name"]
    if bucket:
        try:
            ipaddress.ip_address(bucket)
        except ValueError:
            pass
        else:
            raise ValueError("bucket_name은 IP 주소일 수 없습니다.")
        if ".." in bucket or bucket.startswith(("xn--", "sthree-", "amzn-s3-demo-")) or bucket.endswith(("-s3alias", "--ol-s3", ".mrap", "--x-s3", "--table-s3")):
            raise ValueError("bucket_name에 AWS 예약 이름을 사용할 수 없습니다.")
    arn = config["existing_oidc_provider_arn"]
    if arn and config["aws_account_id"] and arn != f"arn:aws:iam::{config['aws_account_id']}:oidc-provider/app.terraform.io":
        raise ValueError("existing_oidc_provider_arn의 계정이 일치하지 않습니다.")
    if arn and config["create_oidc_provider"]:
        raise ValueError("OIDC 재사용과 새 생성을 동시에 선택할 수 없습니다.")
    return config


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def copy_allowed(source, destination, patterns):
    for pattern in patterns:
        for file in sorted(source.glob(pattern)):
            if file.is_symlink() or not file.resolve().is_relative_to(source.resolve()):
                raise ValueError("게시 원본의 symlink는 허용하지 않습니다.")
            if file.is_file():
                if possible_secret(file.read_text()):
                    raise ValueError("게시 파일에 Secret으로 보이는 내용이 있습니다. 원문은 출력하지 않습니다.")
                target = destination / file.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(file, target)


def archive(directory, output):
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for file in sorted(directory.rglob("*")):
            if file.is_file():
                info = zipfile.ZipInfo(file.relative_to(directory).as_posix(), (2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                package.writestr(info, file.read_bytes())


def prepare(value, destination, root=ROOT):
    config = validate_config(value)
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError("출력은 아직 존재하지 않는 새 디렉터리여야 합니다.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    checks = []
    with tempfile.TemporaryDirectory(prefix="demo-prepare-", dir=destination.parent) as temporary:
        stage = Path(temporary) / "output"
        stage.mkdir()
        packages = stage / "packages"
        module = packages / "terraform-aws-s3-standard"
        policy = packages / "terraform-demo-policies"
        demo = packages / "aws-ai-demo"
        copy_allowed(root / "packages/terraform-aws-s3-standard", module, ["main.tf", "variables.tf", "versions.tf", "outputs.tf", "README.md", ".terraform.lock.hcl", "tests/*.tftest.hcl"])
        copy_allowed(root / "packages/terraform-demo-policies", policy, ["*.sentinel", "sentinel.hcl", "README.md", "mocks/*.sentinel", "test/**/*.hcl"])
        copy_allowed(root / "packages/aws-ai-demo", demo, ["README.md", "templates/*.tmpl", "fixtures/*.patch"])
        for required in [module / "main.tf", module / "variables.tf", module / "versions.tf", module / "outputs.tf", policy / "require-owner.sentinel", policy / "sentinel.hcl", demo / "templates/main.tf.tmpl", demo / "templates/variables.tf.tmpl", demo / "templates/versions.tf.tmpl"]:
            if not required.is_file():
                raise ValueError("게시 원본의 필수 파일이 없습니다.")
        for directory in (module, policy, demo):
            (directory / "AGENTS.md").write_text(
                "# 데모 게시 패키지\n\n설명은 한국어로 작성합니다. Secret/State/Key를 Git에 넣지 않습니다.\n"
                "실제 AWS/HCP 변경은 대상·비용·State·사람의 승인을 확인한 뒤 수행합니다.\n"
                "Module은 Owner 누락을 허용하고 require-owner 정책은 hard-mandatory를 유지합니다.\n"
                "Root만 수정해 Owner 실패/수정 시나리오를 시연하며 정책을 약화하지 않습니다.\n"
            )
        if config["hcp_organization"]:
            for template in (demo / "templates").glob("*.tmpl"):
                text = template.read_text().replace("__HCP_ORGANIZATION__", config["hcp_organization"])
                if config["owner"]:
                    text = text.replace('"demo-team"', json.dumps(config["owner"]))
                (demo / template.name.removesuffix(".tmpl")).write_text(text)
            if config["owner"]:
                for patch in (demo / "fixtures").glob("*.patch"):
                    patch.write_text(patch.read_text().replace('"demo-team"', json.dumps(config["owner"])))
            checks.append({"check": "registry-root", "status": "PASS", "detail": "확인된 입력으로 Root 파일 생성; Registry 게시/다운로드는 미실행"})
        else:
            checks.append({"check": "registry-root", "status": "BLOCKED", "missing": ["hcp_organization"]})
        for name, required in {
            "mcp-host": ["vpc_id", "subnet_id", "ami_id", "owner"],
            "hcp-aws-identity": ["aws_account_id", "hcp_organization", "bucket_name"],
            "workspace": ["hcp_organization", "bucket_name"],
            "client": ["aws_account_id", "mcp_instance_id", "ssm_session_prefix"],
        }.items():
            missing = [key for key in required if not config[key]]
            if name == "hcp-aws-identity" and not (config["existing_oidc_provider_arn"] or config["create_oidc_provider"]):
                missing.append("existing_oidc_provider_arn 또는 승인된 create_oidc_provider")
            checks.append({"check": name + "-inputs", "status": "BLOCKED" if missing else "PASS", "missing": missing, "detail": "파일 준비 상태이며 외부 연결/배포 결과가 아닙니다."})
            if missing:
                continue
            if name == "mcp-host":
                values = {key: config[key] for key in ["aws_region", "vpc_id", "subnet_id", "ami_id", "associate_public_ip_address"]}
                values["tags"] = {"Purpose": "mcp-demo", "Owner": config["owner"]}
                values["ssh_ingress_cidrs"] = []
                write_json(stage / "inputs/mcp-host.tfvars.json", values)
            elif name == "hcp-aws-identity":
                values = {key: config[key] for key in ["aws_region", "aws_account_id", "hcp_organization", "hcp_project", "hcp_workspace", "bucket_name", "create_oidc_provider", "existing_oidc_provider_arn"]}
                write_json(stage / "inputs/hcp-aws-identity.tfvars.json", values)
            elif name == "workspace":
                write_json(stage / "inputs/workspace-settings.json", {
                    "organization": config["hcp_organization"], "project": config["hcp_project"],
                    "workspace": config["hcp_workspace"], "execution_mode": "remote", "auto_apply": False,
                    "terraform_version": "1.13.5", "terraform_variables": {"aws_region": config["aws_region"], "bucket_name": config["bucket_name"]},
                    "required_after_identity_apply": ["TFC_AWS_PLAN_ROLE_ARN", "TFC_AWS_APPLY_ROLE_ARN"],
                    "environment_variables": {"TFC_AWS_PROVIDER_AUTH": "true", "TFC_AWS_WORKLOAD_IDENTITY_AUDIENCE": "aws.workload.identity"},
                })
            else:
                replacements = {"ap-northeast-2": config["aws_region"], "REPLACE_ACCOUNT_ID": config["aws_account_id"], "REPLACE_INSTANCE_ID": config["mcp_instance_id"], "REPLACE_APPROVED_SESSION_PREFIX": config["ssm_session_prefix"]}
                for name in ["iam-ssm-client.json.example", "iam-ssm-operator.json.example"]:
                    text = (root / "client-configs" / name).read_text()
                    for before, after in replacements.items():
                        text = text.replace(before, after)
                    write_json(stage / "inputs" / name.removesuffix(".example"), json.loads(text))
        sums = {}
        for directory in (module, policy, demo):
            output = stage / (directory.name + ".zip")
            archive(directory, output)
            sums[output.name] = hashlib.sha256(output.read_bytes()).hexdigest()
        write_json(stage / "checksums.json", sums)
        checks.insert(0, {"check": "publication-packages", "status": "PASS", "detail": "Module/Root/Policy의 파일 allowlist로 ZIP 3개 생성; 게시는 미실행"})
        write_json(stage / "readiness.json", {"scope": "local-preparation-only", "checks": checks, "external_changes": False})
        (stage / "README.md").write_text(
            "# 로컬 준비 결과\n\nreadiness.json은 파일 생성 상태입니다. 배포/Registry 연결 성공이 아닙니다.\n"
            "ZIP은 게시 검토용입니다. 실제 Repo/Tag/HCP 생성은 수행하지 않았습니다.\n"
            "inputs의 tfvars.json은 검토 후 해당 infra root에 명시적으로 전달합니다.\n"
            "AWS State 저장·잠금·비용·네트워크와 HCP 권한은 운영자가 확인해야 합니다.\n"
        )
        stage.rename(destination)
    return {"scope": "local-preparation-only", "checks": checks, "external_changes": False}
