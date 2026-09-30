# Cloud 준비 완료 범위

2026-09-30 UTC. 기준은 공개 저장소 `Byeongwook-Heo/terraform-ai-mcp-demo`의 main입니다. 사용자는 main 직접 반영과 Phase 2 이후까지 가능한 Cloud 작업을 요청했습니다. Phase 1 PR #1은 이미 병합된 상태에서 이어서 작업했습니다.

**main 게시 PASS.** 연동 앱의 일시 중지가 해제됐고 Git Data API로 구현 Commit `faf4b2ce11222d3546306be1dabfdbf09a9b20e3`를 main에 반영했습니다. 원격 tree와 검토본이 일치하고 fetch 후 파일 diff=0을 확인했습니다. 최신 게시·CI 상태는 `cloud-publication.json`을 확인합니다.

## 구현한 준비물

| 범위 | 산출물 |
|---|---|
| 인프라·인증·호스트 | 기존 EC2/SSM, Plan/Apply OIDC Role, stdio/metadata 차단 코드 보존 |
| 게시 준비 | Module/Root/Policy 파일 allowlist, 독립 AGENTS.md, ZIP 3개와 재현 가능한 SHA256 생성기 |
| 비민감 입력 | 필드/형식/계정 일치 검사, 미정값 null, 계정별 tfvars/Workspace/SSM IAM 파일 생성 |
| 시연 준비 | Registry Root의 Owner 누락/수정 patch, 실제 Sentinel CLI 정상/실패/복구 리허설 |
| MCP 격리 조회 | 실제 고정 Image + loopback Mock Registry의 Module 검색·상세/Version/Input/Output tools/call |
| 재개 | main 기준 README/START_HERE/AGENTS/휴대폰 안내 |
| CI | main push/PR/수동 credential-free 검증과 증거/게시 패키지 artifact |

## 실행 증거

최종 전체 검증 종료 코드 **0**, 검사 **28개 모두 PASS**입니다. Python 단위 테스트 **12개**, Terraform network=none Mock Plan **10개**, Sentinel Mock **12개**, 정상/누락/수정 리허설 **3개**가 통과했습니다. MCP의 허용 도구 6개 및 Mock Module 검색/상세 조회도 통과했습니다.

최신 실행 상태는 `validation-results.json`, 세부 로그는 `validation-logs/`, 시연 정책 결과는 `rehearsal.json`을 기준으로 판단합니다. `cloud-preparation-readiness.json`은 현재 입력으로 생성 가능한 파일과 미정값을 기록합니다. PASS는 각 검사의 범위에 한정됩니다.

GitHub main의 구현 Commit에서도 **[GitHub Actions Run 36679127805](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36679127805) PASS**를 확인했습니다. 도구 설치, 자격증명 없는 전체 검증, 게시 패키지 생성, 증거 artifact 업로드가 모두 성공했습니다. 검증 대상은 구현 Commit `faf4b2ce11222d3546306be1dabfdbf09a9b20e3`이며 후속 상태 보고서 Commit과 구분합니다. [검증 증거·게시 패키지 artifact](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36679127805/artifacts/11080114938)는 CI 보존 기간 14일 동안 제공됩니다.

전체 검증의 정상 종료 코드 0은 모든 검사 PASS입니다. BLOCKED/SKIPPED가 있으면 2, FAIL이 있으면 1입니다. 실제 Private Registry Root는 init하지 않으며 AWS/HCP credentials, 사용자 Terraform 설정을 격리합니다.

## 실제 입력 없어서 완료하지 않은 항목

- AWS account/VPC/Subnet/AMI/egress 및 State 저장·잠금·백업·비용 확인
- 실제 EC2/SSM 접속, AL2023 Docker/iptables 지속성, Token 런타임 주입
- 실제 HCP Organization/entitlement, Registry 게시·다운로드, Workspace/Policy Set 연결
- 실제 OIDC/IAM API 허용, 역할 output과 Workspace 등록
- 별도 AI Client→AWS MCP 연결 및 실제 Private Module 조회
- 실제 Speculative/Standard Run, HCP 정책 실패/수정, 수동 Apply 대기와 S3 결과

이 Cloud 환경에는 AWS/HCP 자격증명이나 위 실제 계정값이 제공되지 않았습니다. 준비 파일과 Mock 결과로 실제 배포/조회가 완료됐다고 판단하지 않습니다. 자세한 입력은 `required-inputs.md`, 실제 실행 순서는 `../docs/09-cloud-preparation.md`를 확인합니다.
