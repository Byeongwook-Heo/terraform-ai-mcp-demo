#!/usr/bin/env python3
"""게시용 ZIP과 입력 파일을 로컬에 생성합니다. 외부 API/Plan/Apply 호출 없음."""
import argparse
import json
from pathlib import Path
from demo_preparation import prepare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prepare(json.loads(args.config.read_text()), args.output)
    except (ValueError, OSError):
        parser.exit(2, "준비 실패: 비민감 입력 형식과 새 출력 디렉터리를 확인하세요. 입력 원문은 출력하지 않습니다.\n")
    for check in result["checks"]:
        print(f"{check['status']}: {check['check']}")
    print("외부 변경 없음. 미정값은 readiness.json에 기록했습니다.")


if __name__ == "__main__":
    main()
