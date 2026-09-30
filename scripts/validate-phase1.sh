#!/usr/bin/env bash
set -euo pipefail
repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
# 추가 인수를 받지 않으며 live 검증이나 apply를 호출하지 않습니다.
[[ $# -eq 0 ]] || exit 2
exec python3 "$repo_dir/scripts/validate-phase1.py"
