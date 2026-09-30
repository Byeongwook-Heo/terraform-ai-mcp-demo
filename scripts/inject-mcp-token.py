#!/usr/bin/env python3
"""Phase 2 운영자 전용. getpass로 읽고 /run의 Root 0600 파일만 기록합니다."""
import getpass
import os
import stat
import sys
from pathlib import Path

def main():
    if os.geteuid() != 0 or len(sys.argv) != 1:
        raise SystemExit("승인된 EC2에서 root로 인수 없이 실행하세요.")
    directory = Path("/run/terraform-mcp")
    directory.mkdir(mode=0o700, exist_ok=True)
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o700:
        raise SystemExit("런타임 디렉터리 권한이 안전하지 않습니다.")
    # Terminal 없을 때 fallback으로 echo되는 입력을 금지합니다.
    with open("/dev/tty", "r+") as terminal:
        token = getpass.getpass("조회 전용 HCP Token (화면에 표시하지 않음): ", stream=terminal)
    if not token or any(c.isspace() or ord(c) < 32 for c in token) or len(token) > 16384:
        raise SystemExit("Token 형식을 확인하세요.")
    os.umask(0o077)
    temp = directory / "token.new"
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as output:
        output.write(token)
    os.replace(temp, directory / "token")
    print("런타임 Token 주입 완료. 재부팅 뒤 다시 주입해야 합니다.", file=sys.stderr)

if __name__ == "__main__":
    main()
