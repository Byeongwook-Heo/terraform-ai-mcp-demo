#!/usr/bin/env python3
"""Registry root를 로컬 새 디렉터리에만 렌더링합니다. init/외부 호출은 없습니다."""
import argparse
import re
from pathlib import Path

def render(organization, destination):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", organization):
        raise ValueError("Organization 형식을 확인하세요.")
    templates = Path(__file__).resolve().parents[1] / "packages/aws-ai-demo/templates"
    destination.mkdir(parents=True, exist_ok=False)
    for source in templates.glob("*.tf.tmpl"):
        (destination / source.name.removesuffix(".tmpl")).write_text(source.read_text().replace("__HCP_ORGANIZATION__", organization))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--organization", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render(args.organization, args.output)
