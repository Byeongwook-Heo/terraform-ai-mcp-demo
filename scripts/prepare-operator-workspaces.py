#!/usr/bin/env python3
"""Host/Identity 검토 Root와 비활성 HCP State 설정 생성. API/Plan/Apply 호출 없음."""
import argparse
import json
from pathlib import Path

from operator_preparation import prepare_operator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        prepare_operator(json.loads(args.config.read_text()), args.output)
    except (ValueError, OSError):
        parser.exit(2, "운영 준비 실패: 확인된 비민감 입력과 새 출력 디렉터리를 확인하세요. 원문은 출력하지 않습니다.\n")
    print("PASS: Host/Identity 검토 Root와 별도 State 설정 생성. 외부 변경 없음; 실제 Apply 승인이 아닙니다.")


if __name__ == "__main__":
    main()
