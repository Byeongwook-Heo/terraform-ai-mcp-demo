#!/usr/bin/env bash
set -euo pipefail
repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
# 인수는 Python argparse에서 검사하며 live 검증이나 apply를 호출하지 않습니다.
exec python3 "$repo_dir/scripts/validate-phase1.py" "$@"
