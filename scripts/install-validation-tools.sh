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
# Cloud와 CI에서 같은 ShellCheck 버전을 사용합니다. 공식 release asset를 고정합니다.
shellcheck_archive="$venv_dir/shellcheck.tar.xz"
curl --fail --silent --show-error --location \
  https://github.com/koalaman/shellcheck/releases/download/v0.10.0/shellcheck-v0.10.0.linux.x86_64.tar.xz \
  -o "$shellcheck_archive"
printf '6c881ab0698e4e6ea235245f22832860544f17ba386442fe7e9d629f8cbedf87  %s\n' "$shellcheck_archive" | sha256sum -c -
tar -xJf "$shellcheck_archive" --strip-components=1 -C "$tool_dir" shellcheck-v0.10.0/shellcheck
if [[ -n ${GITHUB_PATH:-} ]]; then
  printf '%s\n' "$tool_dir" >> "$GITHUB_PATH"
else
  printf '검증 실행 PATH에 추가할 경로: %s\n' "$tool_dir"
fi
