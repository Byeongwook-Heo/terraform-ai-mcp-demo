# 지금 이어서 시작하기

기준은 공개 저장소 **Byeongwook-Heo/terraform-ai-mcp-demo의 main**입니다. Phase 1은 PR #1로 병합됐고, 사용자는 main에 결과를 두고 Phase 2 이후의 Cloud 준비도 완료하도록 요청했습니다.

1. Codex Cloud에서 이 저장소와 main을 선택합니다.
2. `AGENTS.md`, `DEMO_SPEC.md`, `reports/cloud-completion.md`, `reports/progress.md`를 읽습니다.
3. 계정 없이 가능한 코드·패키지·문서·격리 검증을 진행하고 main에 게시합니다.
4. 실제 계정 입력과 접근권한이 필요한 항목은 `reports/required-inputs.md`에서 확인합니다. Secret은 채팅/Git에 적지 않습니다.

```text
terraform-ai-mcp-demo 저장소의 최신 main에서 이어서 작업해줘.
AGENTS.md, DEMO_SPEC.md와 reports/cloud-completion.md를 먼저 읽어줘.
Cloud에서 가능한 준비와 검증을 모두 완료하고 main에 반영해줘.
기존 결과를 보존하고 미정인 AWS/HCP 값을 추측하지 마.
실제 연결 결과와 Mock 검증 결과는 구분해서 보고해줘.
```

## 계정 없이 실행하는 준비

```bash
bash scripts/install-validation-tools.sh
# 로컬에서는 설치 스크립트가 안내한 디렉터리를 PATH에 추가합니다.
bash scripts/validate-phase1.sh
python3 scripts/prepare-demo.py --config configs/demo-inputs.example.json --output .artifacts/prepared
python3 scripts/verify-prepared-demo.py --prepared .artifacts/prepared
```

`validate-phase1.sh`의 파일명은 기존 문서와 호환되게 유지합니다. 현재는 Terraform/Sentinel/MCP 격리 검증, 시연 리허설과 게시 패키지 생성·검증을 함께 수행합니다. ZIP과 SHA256은 `.artifacts/prepared/`, 파일 준비 상태는 `readiness.json`에 있습니다. 다운로드한 ZIP을 검사할 때는 ZIP 3개, `checksums.json`, `readiness.json`을 같은 디렉터리에 모아 검증기에 지정합니다. 입력 미정에 따른 BLOCKED와 ZIP 검사 PASS는 서로 다른 결과이며 실제 배포를 의미하지 않습니다.

전체 검증에는 Linux x86_64, Python 3.11 이상, ShellCheck와 Docker daemon이 필요합니다. 도구 또는 네트워크가 없으면 PASS로 처리하지 않습니다. 더 자세한 실행 순서는 [Cloud 준비 안내](docs/09-cloud-preparation.md)에 있습니다.

## 위임된 운영 기본값과 실제 계정 검토

네트워크·State·Owner/Bucket 선택은 완료했으며 같은 값을 다시 요청하지 않습니다. 비민감 입력은 Git 제외 configs/demo-inputs.local.json에 있습니다. Host/Identity 실제 읽기 전용 Plan과 [HCP Local State 준비](docs/10-operator-state-and-review.md)를 완료했습니다. 실제 변경 승인은 별도로 확인하며 검토 Plan은 Apply하지 않습니다.
