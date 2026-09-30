#!/usr/bin/env bash
set -euo pipefail
# Phase 2 EC2 user_data 전용. Secret과 MCP HTTP 서비스가 없습니다.
# 이름 제한은 OS 호환성을 보장하지 않습니다. 패키지/서비스 변경 전에 확인합니다.
source /etc/os-release
if [[ ${ID:-} != amzn || ${VERSION_ID:-} != 2023 ]]; then
  printf '%s\n' '현재 bootstrap은 Amazon Linux 2023 전용입니다. 승인 AMI의 OS를 확인하세요.' >&2
  exit 1
fi
dnf install -y docker python3 iptables-nft
systemctl enable --now docker
if ! rpm -q amazon-ssm-agent >/dev/null; then
  printf '%s\n' 'SSM Agent가 없는 AMI입니다. 승인된 AL2023 AMI를 확인하세요.' >&2
  exit 1
fi
systemctl enable --now amazon-ssm-agent
