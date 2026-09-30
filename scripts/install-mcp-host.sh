#!/usr/bin/env bash
set -euo pipefail
# Phase 2 승인된 EC2에서만 실행. 인수는 공개 SSH key 파일 경로입니다.
[[ $EUID -eq 0 && $# -eq 1 ]] || { printf '%s\n' 'root와 공개 SSH key 파일 인수가 필요합니다.' >&2; exit 2; }
repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
public_key_file=$1
[[ -f "$public_key_file" ]] || exit 2
# command=, options, 다중 키 등은 받지 않습니다.
/usr/bin/python3 - "$public_key_file" <<'KEY'
import re,sys
from pathlib import Path
key=Path(sys.argv[1]).read_text().strip()
if not re.fullmatch(r"ssh-ed25519 [A-Za-z0-9+/=]+(?: [^\r\n]+)?",key):
    raise SystemExit("일반 ssh-ed25519 공개 key 한 줄만 허용합니다.")
KEY
install -d -o root -g root -m 0755 /opt/terraform-mcp
install -o root -g root -m 0755 "$repo_dir/services/terraform-mcp/launch.sh" "$repo_dir/services/terraform-mcp/launch.py" "$repo_dir/services/terraform-mcp/network-guard.sh" /opt/terraform-mcp/
install -o root -g root -m 0644 "$repo_dir/services/terraform-mcp/config.json" /opt/terraform-mcp/
install -o root -g root -m 0644 "$repo_dir/services/terraform-mcp/mcp-network-guard.service" /etc/systemd/system/
image=$(/usr/bin/python3 -c 'import json;print(json.load(open("/opt/terraform-mcp/config.json"))["image"])')
/usr/bin/docker pull "$image" >&2
id mcp-client >/dev/null 2>&1 || useradd --create-home --shell /bin/bash mcp-client
# 전용 계정의 home/authorized_keys를 Root 소유로 고정해 forced command 변경을 막습니다.
chown root:root /home/mcp-client
chmod 0755 /home/mcp-client
install -d -o root -g root -m 0755 /home/mcp-client/.ssh
{ printf '%s' 'restrict,command="sudo -n /opt/terraform-mcp/launch.sh" '; cat "$public_key_file"; printf '\n'; } > /home/mcp-client/.ssh/authorized_keys
chown root:root /home/mcp-client/.ssh/authorized_keys
# sshd는 사용자 권한으로 공개키를 읽습니다. Root 소유와 쓰기 제한은 유지합니다.
chmod 0644 /home/mcp-client/.ssh/authorized_keys
printf '%s\n' 'mcp-client ALL=(root) NOPASSWD: /opt/terraform-mcp/launch.sh ""' > /etc/sudoers.d/terraform-mcp
chmod 0440 /etc/sudoers.d/terraform-mcp
visudo -cf /etc/sudoers.d/terraform-mcp
install -d -o root -g root -m 0700 /run/terraform-mcp
systemctl daemon-reload
systemctl enable --now mcp-network-guard.service
systemctl enable --now sshd
printf '%s\n' '설치 완료. Token 주입, sshd 계정 제한과 SSM 터널 검증은 별도입니다.' >&2
