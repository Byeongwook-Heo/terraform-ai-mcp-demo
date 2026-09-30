# 휴대폰에서 main으로 이어서 작업하기

현재 기준은 공개 저장소 **[terraform-ai-mcp-demo의 main](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/tree/main)**입니다. Phase 1 PR #1은 이미 병합됐습니다. 예전 작업 Branch를 선택할 필요 없이 main을 선택해 후속 작업을 시작합니다.

## 지금 확인할 것

| 작업 | 휴대폰에서 확인할 곳 | 현재 상태 |
|---|---|---|
| 준비 코드·문서 | 저장소 main | Phase 1 및 후속 Cloud 준비 |
| 완료·남은 입력 | `reports/cloud-completion.md`, `reports/required-inputs.md` | 계정 없는 검사와 실환경 조건 구분 |
| CI와 게시 패키지 | GitHub Actions의 Cloud preparation workflow | main push/PR/수동 검증; 실제 Run 상태 확인 |
| Cloud 재개 | Codex Cloud 저장소 선택 | 이 저장소의 main |
| 실환경 입력 파일 | `configs/demo-inputs.example.json` | 미정값은 null, 실제 값은 local 복사본 |
| 시연 순서 | `docs/05-demo-and-recording.md` | 조회 → Policy 실패/수정 → 리뷰 → Standard Run/승인 |

GitHub Actions가 성공하면 Run의 artifact에서 검증 보고서와 게시용 ZIP을 받을 수 있습니다. 원격 CI 성공은 실제 Run의 conclusion으로만 판단합니다. Cloud 로컬 검증 성공과 별개입니다.

ZIP을 받은 뒤 Cloud의 Python 실행 환경에서 검사할 수 있습니다. ZIP 3개와 `checksums.json`, `readiness.json`을 같은 디렉터리에 모으고 `python3 scripts/verify-prepared-demo.py --prepared <해당 디렉터리>`를 실행합니다. 파일을 압축 해제하거나 AWS/HCP에 접속하지 않습니다. checksum의 출처는 성공한 CI Run/Commit과 대조하세요. 상세 범위는 [Cloud 준비](09-cloud-preparation.md)에 있습니다.

## PC 없이 가능한 실제 환경 확인

운영자가 휴대폰에서 AWS/HCP 웹에 로그인해 비민감 값과 접근 조건을 확인합니다. Codex에 Token이나 AWS Key를 채팅으로 보낼 필요가 없습니다.

- AWS account/Region/VPC/Subnet/AL2023 AMI, egress와 SSM 연결 조건
- HCP Organization/Project/Workspace, Sentinel entitlement와 VCS/Registry 권한
- Bucket 이름·Owner 값, State 저장·잠금·복구, 비용과 정리 담당자
- 게시 저장소/Module version, PR 리뷰·Apply 담당자

확인된 값으로 Cloud에서 생성기를 다시 실행하면 입력 파일을 준비할 수 있습니다. 파일 생성은 외부 리소스 변경을 수행하지 않습니다. 자세한 명령과 준비 결과는 [Cloud 준비](09-cloud-preparation.md)에 있습니다.

휴대폰 AWS Console 또는 승인된 CloudShell에서 환경을 준비할 수 있지만 브라우저 Shell은 호스트 관리 경로입니다. 실제 MCP 시연에는 별도 Codex CLI/IDE 실행 환경, AWS CLI/Session Manager plugin, SSH key/검증한 host key가 필요합니다. Cloud 저장소 연결만으로 이 연결이 생기지 않습니다.

## 다음 작업 요청

```text
terraform-ai-mcp-demo의 main에서 이어서 작업해줘.
reports/cloud-completion.md의 미완료 항목과 required-inputs.md를 확인해줘.
내가 확인한 비민감 값만 사용해 준비 파일을 갱신하고 main에 반영해줘.
실제 연결 검증은 사용할 수 있는 자격증명·대상·접근 환경을 확인한 뒤 진행해줘.
```

Token/Access Key/Private Key/State 원문은 이 메모와 Git에 넣지 않습니다. 실제 S3 Apply는 PR Merge 후 새로운 Standard Run에서 Plan·Policy를 다시 확인하고 담당자가 승인합니다.
