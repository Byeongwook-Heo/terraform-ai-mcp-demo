#!/usr/bin/env python3
"""Root 전용 고정 stdio 런처. Token 값은 argv/stdout/log에 출력하지 않습니다."""
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

CONFIG = Path("/opt/terraform-mcp/config.json")
TOKEN = Path("/run/terraform-mcp/token")
EXPECTED_TOOLS = {
    "search_private_modules", "get_private_module_details", "list_workspaces",
    "list_runs", "get_run_details", "get_token_permissions",
}
IMAGE = "hashicorp/terraform-mcp-server:1.3.0@sha256:423a6b8e2ee06affcf090892f40c86469caba45fd2448ffa8ca5d717a174f7d5"
FIREWALL_CHECKS = [
    ["/usr/sbin/iptables", "-C", "DOCKER-USER", "-s", "172.30.240.0/24", "-d", "169.254.0.0/16", "-j", "REJECT"],
    ["/usr/sbin/iptables", "-C", "INPUT", "-i", "mcp0", "-j", "REJECT"],
]

def read_token(path, owner_uid=0):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != owner_uid or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1:
            raise ValueError("unsafe token file")
        with os.fdopen(fd, "r", closefd=False) as stream:
            token = stream.read(16385).rstrip("\n")
        if not token or len(token) > 16384 or any(c.isspace() or ord(c) < 32 for c in token):
            raise ValueError("invalid token file")
        return token
    finally:
        os.close(fd)

def build_command(config):
    if config != {"image": IMAGE, "tfe_address": "https://app.terraform.io", "tools": config.get("tools")} or set(config["tools"]) != EXPECTED_TOOLS or len(config["tools"]) != len(EXPECTED_TOOLS):
        raise ValueError("unapproved configuration")
    return [
        "/usr/bin/docker", "run", "--rm", "--pull=never", "-i",
        "--network", "mcp-isolated", "--user", "65532:65532", "--read-only",
        "--cap-drop=ALL", "--security-opt=no-new-privileges", "--pids-limit=128",
        "--memory=512m", "--cpus=1", "--log-driver=none",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m", "-e", "TFE_TOKEN",
        "-e", "TFE_ADDRESS=https://app.terraform.io", "-e", "ENABLE_TF_OPERATIONS=false",
        "-e", "TFE_SKIP_TLS_VERIFY=false", "-e", "TRANSPORT_MODE=stdio",
        "-e", "OTEL_METRICS_ENABLED=false", "-e", "INSTANA_ENABLED=false",
        IMAGE, "stdio", "--log-level=error", "--tools=" + ",".join(config["tools"]),
    ]

def main():
    try:
        if os.geteuid() != 0 or len(sys.argv) != 1:
            raise ValueError("root fixed launcher required")
        env = {"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "HOME": "/root"}
        for check in FIREWALL_CHECKS:
            subprocess.run(check, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        # Docker network의 설정 변경은 호스트 관리자의 권한입니다.
        result = subprocess.run(["/usr/bin/docker", "network", "inspect", "mcp-isolated"], check=True, capture_output=True, env=env)
        network = json.loads(result.stdout)[0]
        if network["Driver"] != "bridge" or network["EnableIPv6"] or network["IPAM"]["Config"][0]["Subnet"] != "172.30.240.0/24" or network["Options"].get("com.docker.network.bridge.name") != "mcp0":
            raise ValueError("unapproved Docker network")
        config = json.loads(CONFIG.read_text())
        command = build_command(config)
        env["TFE_TOKEN"] = read_token(TOKEN)
    except Exception:
        print("MCP 시작 차단: 설치, 방화벽, 설정 또는 런타임 Token 권한을 확인하세요.", file=sys.stderr)
        return 1
    os.execve(command[0], command, env)

if __name__ == "__main__":
    sys.exit(main())
