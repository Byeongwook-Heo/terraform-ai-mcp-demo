#!/usr/bin/env python3
"""게시 ZIP 3개와 checksums/readiness 검사. 파일 압축 해제와 외부 호출 없음."""
import argparse
import json
from pathlib import Path

from publication_verification import verify_prepared


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify_prepared(args.prepared)
    except (ValueError, OSError):
        parser.exit(1, "FAIL: 게시 패키지 검증 실패. ZIP·checksum·readiness와 허용 파일 조건을 확인하세요. 원문은 출력하지 않습니다.\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("PASS: ZIP 검사 완료. 실제 Registry 게시·AWS/HCP 배포 검증과는 별개입니다.")


if __name__ == "__main__":
    main()
