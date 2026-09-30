#!/usr/bin/env bash
set -euo pipefail
# Phase 2 EC2 user_data 전용. Secret과 MCP HTTP 서비스가 없습니다.
dnf install -y docker python3 iptables-nft
systemctl enable --now docker
if ! rpm -q amazon-ssm-agent >/dev/null; then
  printf '%s\n' 'SSM Agent가 없는 AMI입니다. 승인된 AL2023 AMI를 확인하세요.' >&2
  exit 1
fi
systemctl enable --now amazon-ssm-agent
