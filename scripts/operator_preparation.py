"""실제 Plan 검토용 Root와 별도 HCP State 설정을 준비합니다. 외부 호출 없음."""
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import hcl2

from demo_preparation import ROOT, copy_allowed, prepare, validate_config, write_json

STATE_WORKSPACES = {
    "mcp-host": "mcp-host-state",
    "hcp-aws-identity": "hcp-aws-identity-state",
}
ROOT_FILES = ["main.tf", "variables.tf", "versions.tf", "outputs.tf", ".terraform.lock.hcl"]


def prepare_operator(value, destination, root=ROOT):
    config = validate_config(value)
    required = ["aws_account_id", "hcp_organization", "vpc_id", "subnet_id", "ami_id", "owner", "bucket_name"]
    if any(not config[key] for key in required):
        raise ValueError("Host/Identity의 확인된 비민감 입력이 필요합니다.")
    if not (config["create_oidc_provider"] or config["existing_oidc_provider_arn"]):
        raise ValueError("OIDC 생성 또는 재사용 계획이 필요합니다. 파일 생성은 실제 생성 승인이 아닙니다.")
    if config["hcp_workspace"] in STATE_WORKSPACES.values():
        raise ValueError("Remote 데모 Workspace와 Local State Workspace를 분리하세요.")
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError("출력은 아직 존재하지 않는 새 디렉터리여야 합니다.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="operator-prepare-", dir=destination.parent) as temporary:
        stage = Path(temporary) / "output"
        stage.mkdir(mode=0o700)
        prepare(config, stage / "publication", root=root)
        settings = []
        for name, workspace in STATE_WORKSPACES.items():
            source = root / "infra" / name
            if source.is_symlink() or not source.resolve().is_relative_to(root.resolve()):
                raise ValueError("Root 원본은 프로젝트 내부의 실제 디렉터리여야 합니다.")
            files = ROOT_FILES + (["bootstrap.sh"] if name == "mcp-host" else [])
            if not all((source / file).is_file() for file in files):
                raise ValueError("Root 필수 파일이 없습니다.")
            review = stage / "review" / name
            copy_allowed(source, review, files)
            for file in review.glob("*.tf"):
                for terraform in hcl2.loads(file.read_text()).get("terraform", []):
                    if "cloud" in terraform or "backend" in terraform:
                        raise ValueError("검토 Root의 활성 외부 State 설정은 허용하지 않습니다.")
            shutil.copyfile(stage / "publication/inputs" / (name + ".tfvars.json"), review / "inputs.tfvars.json")
            overlay = stage / "state-overlays" / name / "backend.tf"
            overlay.parent.mkdir(parents=True)
            overlay.write_text(
                "# Workspace를 승인된 범위로 먼저 생성한 뒤 배포 Root에만 복사합니다.\n"
                "terraform {\n  cloud {\n"
                f"    organization = {json.dumps(config['hcp_organization'])}\n"
                f"    workspaces {{\n      name = {json.dumps(workspace)}\n    }}\n"
                "  }\n}\n"
            )
            settings.append({
                "organization": config["hcp_organization"], "project": config["hcp_project"],
                "workspace": workspace, "execution_mode": "local", "auto_apply": False,
                "terraform_version": "1.13.5", "purpose": name + " State/lock/version history",
                "aws_credentials_in_workspace": False, "global_remote_state": False,
            })
        write_json(stage / "hcp-state-settings.json", settings)
        hashes = {
            file.relative_to(stage).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
            for folder in ("review", "state-overlays")
            for file in sorted((stage / folder).rglob("*")) if file.is_file()
        }
        manifest = {
            "scope": "operator-preparation-only", "external_changes": False,
            "review_state": "isolated-empty-local-state", "review_plan_apply_allowed": False,
            "state_workspace_creation": "pending-scoped-approval",
            "checksums": hashes,
        }
        write_json(stage / "manifest.json", manifest)
        (stage / "README.md").write_text(
            "# 운영 준비\n\n"
            "review/는 기존 State를 읽지 않는 신규 자원 검토용 사본입니다. 실제 Apply용이 아닙니다.\n"
            "terraform init -backend=false -input=false 후\n"
            "terraform plan -input=false -var-file=inputs.tfvars.json 으로 검토합니다.\n"
            "init은 고정 Provider의 공식 체크섬 확인 후 사본 lockfile에 현재 플랫폼 hash를 추가할 수 있습니다.\n"
            "state-overlays/는 자동 활성화하지 않습니다. 승인 뒤 별도 배포 Root에 복사하고,\n"
            "HCP Local Workspace 존재와 State 충돌을 확인한 뒤 init 및 새 Plan을 수행합니다.\n"
            "Local 실행은 HCP Workspace 변수/Variable Set을 사용하지 않습니다. AWS 임시 자격증명은\n"
            "운영자 프로세스 환경에만 전달하며 State/파일/Git/HCP 변수에 저장하지 않습니다.\n"
            "데모 aws-ai-demo는 Sentinel 평가를 위해 별도의 Remote 실행을 유지합니다.\n"
        )
        stage.rename(destination)
    return manifest
