#!/usr/bin/env bash
set -euo pipefail
# Linux x86_64 검증 도구만 설치합니다. AWS/HCP 인증을 사용하지 않습니다.
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || exit 2
repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
venv_dir=$(mktemp -d)
python3 -m venv "$venv_dir/venv"
"$venv_dir/venv/bin/pip" install --disable-pip-version-check -r "$repo_dir/scripts/requirements-validation.txt"
tool_dir="$venv_dir/venv/bin"
for product_version in terraform:1.13.5 sentinel:0.40.0; do
  product=${product_version%%:*}
  version=${product_version##*:}
  archive="${product}_${version}_linux_amd64.zip"
  curl --fail --silent --show-error --location "https://releases.hashicorp.com/$product/$version/$archive" -o "$venv_dir/$archive"
  curl --fail --silent --show-error --location "https://releases.hashicorp.com/$product/$version/${product}_${version}_SHA256SUMS" -o "$venv_dir/$product.sums"
  (cd "$venv_dir"; awk -v file="$archive" '$2 == file { print }' "$product.sums" | sha256sum -c -)
  unzip -qo "$venv_dir/$archive" "$product" -d "$tool_dir"
done
# Ubuntu runner에 ShellCheck가 있어야 합니다. 없으면 성공으로 처리하지 않습니다.
command -v shellcheck >/dev/null
if [[ -n ${GITHUB_PATH:-} ]]; then
  printf '%s\n' "$tool_dir" >> "$GITHUB_PATH"
else
  printf '검증 실행 PATH에 추가할 경로: %s\n' "$tool_dir"
fi
