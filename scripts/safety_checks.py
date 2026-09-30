"""자격증명 없는 검증 대상만 통과시키는 Terraform preflight입니다."""
import json
import tomllib
from pathlib import Path
import hcl2
from secret_patterns import possible_secret

ROOTS = ["infra/mcp-host", "infra/hcp-aws-identity", "packages/terraform-aws-s3-standard", "tests/local-module"]
TOOLS = {"search_private_modules", "get_private_module_details", "list_workspaces", "list_runs", "get_run_details", "get_token_permissions"}

def preflight_test(path):
    body = hcl2.loads(path.read_text())
    if set(body) - {"mock_provider", "variables", "run"}:
        raise ValueError("unsupported test blocks")
    mocks = body.get("mock_provider", [])
    if mocks != [{"aws": {}}] or not body.get("run"):
        raise ValueError("only the default mocked aws provider is permitted")
    for item in body["run"]:
        for run in item.values():
            if run.get("command") != "${plan}" or set(run) - {"command", "variables", "assert", "expect_failures"}:
                raise ValueError("every run must explicitly use command=plan and the default mock provider")

def preflight(root):
    count = 0
    for directory in ROOTS:
        for path in (root / directory).glob("*.tf"):
            body = hcl2.loads(path.read_text())
            if set(body) - {"terraform", "provider", "variable", "resource", "module", "output", "locals"}:
                raise ValueError("unsupported root blocks")
            if "data" in body:
                raise ValueError("data sources are not allowed in Phase 1 test roots")
            for terraform in body.get("terraform", []):
                if "backend" in terraform or "cloud" in terraform:
                    raise ValueError("external state connections are not allowed")
                for providers in terraform.get("required_providers", []):
                    if set(providers) != {"aws"} or providers["aws"].get("source") != "hashicorp/aws":
                        raise ValueError("unexpected provider")
            for provider in body.get("provider", []):
                if set(provider) != {"aws"} or set(provider["aws"]) - {"region"}:
                    raise ValueError("unexpected provider configuration")
            for entry in body.get("resource", []):
                for kind, resources in entry.items():
                    if not kind.startswith("aws_"):
                        raise ValueError("only mocked AWS resources are permitted")
                    for resource in resources.values():
                        if "provisioner" in resource or "connection" in resource or "provider" in resource:
                            raise ValueError("resource execution or real provider override refused")
            for entry in body.get("module", []):
                for module in entry.values():
                    source = module.get("source", "")
                    if not source.startswith("./") and not source.startswith("../"):
                        raise ValueError("registry modules cannot be initialized in Phase 1 validation")
                    resolved = (path.parent / source).resolve()
                    if resolved != (root / "packages/terraform-aws-s3-standard").resolve() or "providers" in module:
                        raise ValueError("unexpected local module or provider override")
        tests = sorted((root / directory).rglob("*.tftest.hcl"))
        if not tests or list((root / directory).rglob("*.tftest.json")):
            raise ValueError("missing reviewed HCL tests or unsupported JSON tests")
        for path in tests:
            preflight_test(path)
            count += len(hcl2.loads(path.read_text())["run"])
    return count

def static_checks(root):
    for path in root.rglob("*"):
        if not path.is_file() or any(x in path.parts for x in [".git", ".terraform", ".validation", ".artifacts", "__pycache__"]):
            continue
        name = path.name
        if name.endswith(".toml.example"):
            config = tomllib.loads(path.read_text())
            server = config["mcp_servers"]["terraform_private"]
            if set(server["enabled_tools"]) != TOOLS or server.get("env") or server["command"] != "ssh":
                raise ValueError("unsafe Codex MCP config")
        if name.endswith(".json") or name.endswith(".json.example"):
            json.loads(path.read_text())
        text = path.read_text(errors="ignore")
        # 실제 값과 유사한 Secret 패턴만 탐지합니다. 내용 자체는 출력하지 않습니다.
        if possible_secret(text):
            raise ValueError("possible secret in " + str(path.relative_to(root)))
    config = json.loads((root / "services/terraform-mcp/config.json").read_text())
    if set(config["tools"]) != TOOLS or ":1.3.0@sha256:" not in config["image"]:
        raise ValueError("unpinned image or expanded tool allowlist")
