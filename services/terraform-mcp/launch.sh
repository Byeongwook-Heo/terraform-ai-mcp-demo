#!/bin/bash
set -euo pipefail
if [[ $# -ne 0 ]]; then
  printf '%s\n' '추가 인수는 허용하지 않습니다.' >&2
  exit 2
fi
exec /usr/bin/python3 -I /opt/terraform-mcp/launch.py
