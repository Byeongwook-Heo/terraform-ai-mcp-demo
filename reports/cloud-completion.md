# Cloud 준비 완료 범위

최신 상태: 2026-09-30 운영 기본값 선택을 위임받아 기존 Private Subnet/허용 AL2023 AMI/HCP Local State/Owner·Bucket 이름을 준비했습니다. 실제 계정의 Host 6개/Identity 5개 신규 Plan(init/validate 포함) PASS, 수정·삭제 0개. Python 24개/ZIP/정적 검사 PASS. AWS/HCP 생성·Apply·MCP 실연결은 미수행이며 구체적인 첫 생성 범위만 승인 대기입니다. operator-preparation-20260930.json과 docs/10-operator-state-and-review.md를 확인합니다. 아래 기록은 해당 시점의 이력입니다.


최신 상태: 2026-09-30 사용자가 명시적으로 승인한 AWS STS/EC2 AMI와 HCP 조직 읽기 전용 조회 및 재대조 PASS. ZIP의 지침 3개를 읽었고 ZIP에 없는 보고서 2개는 main에서 확인했습니다. 실제 리소스/설정 변경은 없으며 필요한 배포 입력은 여전히 미정입니다. 새 비식별 증거는 read-only-discovery-20260930.json 및 progress.md 마지막 기록을 확인합니다. 이전 BLOCKED는 과거 상태입니다.

최신 추가 검증: AMI 보완 Commit `c404c34`의 [Run 36688256340](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36688256340)은 29개 검사 PASS입니다. Python 20개/Mock Plan 14개를 다운로드 artifact로 대조했고 ZIP 재검사도 PASS입니다. 기존 Cloud 보고서와 별도로 ami-ci-evidence-20260930에 보존했습니다. 실제 AWS/HCP 조회·변경과 추가 handoff ZIP 읽기는 BLOCKED입니다. 아래 이전 보고서는 해당 작업 당시의 이력입니다.

2026-09-30 KST(Asia/Seoul). 기준은 공개 저장소 `Byeongwook-Heo/terraform-ai-mcp-demo`의 main입니다. 사용자는 main 직접 반영과 Phase 번호와 관계없이 가능한 Cloud 작업을 이어가도록 요청했습니다. Phase 1 PR #1은 이미 병합된 상태에서 이어서 작업했습니다.

**main 게시 PASS.** 연동 앱의 일시 중지가 해제됐고 Git Data API로 구현 Commit `faf4b2ce11222d3546306be1dabfdbf09a9b20e3`를 main에 반영했습니다. 원격 tree와 검토본이 일치하고 fetch 후 파일 diff=0을 확인했습니다. 최신 게시·CI 상태는 `cloud-publication.json`을 확인합니다.

이후 ZIP 검증기와 최신 상태 안내를 추가한 Commit `fbb9bcc6e94c708c5300f1cd6366326727f5ac97`도 main에 직접 게시했고, **[최신 CI Run 36681296227](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36681296227) PASS**를 확인했습니다. 이번 보완의 게시·검사·다운로드 제한은 `main-continuation.json`에 있습니다.

## 구현한 준비물

| 범위 | 산출물 |
|---|---|
| 인프라·인증·호스트 | 기존 EC2/SSM, Plan/Apply OIDC Role, stdio/metadata 차단 코드 보존 |
| 게시 준비 | Module/Root/Policy 파일 allowlist, 독립 AGENTS.md, ZIP 3개와 재현 가능한 SHA256 생성기 |
| 게시물 확인 | 다운로드한 ZIP 3개의 SHA256·필수 파일·경로·형식·Secret 패턴 검사, 압축 해제와 외부 호출 없음 |
| 비민감 입력 | 필드/형식/계정 일치 검사, 미정값 null, 계정별 tfvars/Workspace/SSM IAM 파일 생성 |
| 시연 준비 | Registry Root의 Owner 누락/수정 patch, 실제 Sentinel CLI 정상/실패/복구 리허설 |
| MCP 격리 조회 | 실제 고정 Image + loopback Mock Registry의 Module 검색·상세/Version/Input/Output tools/call |
| 재개 | main 기준 README/START_HERE/AGENTS/휴대폰 안내 |
| CI | main push/PR/수동 credential-free 검증과 증거/게시 패키지 artifact |

## 실행 증거

최신 로컬 전체 검증 종료 코드 **0**, 검사 **29개 모두 PASS**입니다. Python 단위 테스트 **17개**, Terraform network=none Mock Plan **10개**, Sentinel Mock **12개**, 정상/누락/수정 리허설 **3개**가 통과했습니다. MCP의 허용 도구 6개 및 Mock Module 검색/상세 조회도 통과했습니다. ZIP 무결성·내용 검사가 전체 검증에 추가됐습니다.

최신 실행 상태는 `validation-results.json`, 세부 로그는 `validation-logs/`, 시연 정책 결과는 `rehearsal.json`을 기준으로 판단합니다. `cloud-preparation-readiness.json`은 현재 입력으로 생성 가능한 파일과 미정값을 기록합니다. PASS는 각 검사의 범위에 한정됩니다.

GitHub main의 구현 Commit에서도 **[GitHub Actions Run 36679127805](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36679127805) PASS**를 확인했습니다. 도구 설치, 자격증명 없는 전체 검증, 게시 패키지 생성, 증거 artifact 업로드가 모두 성공했습니다. 검증 대상은 구현 Commit `faf4b2ce11222d3546306be1dabfdbf09a9b20e3`이며 후속 상태 보고서 Commit과 구분합니다. [검증 증거·게시 패키지 artifact](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36679127805/artifacts/11080114938)는 CI 보존 기간 14일 동안 제공됩니다.

위 Run은 검증기 추가 전의 28개 검사·12개 단위 테스트를 검증한 기록입니다. ZIP 검증기를 포함한 최신 코드의 Run 36681296227은 completed/success이며 전체 검증·패키지 생성·증거 업로드 Step도 success입니다. 원격 CI API와 gh run watch --exit-status 종료 코드 0으로 확인했습니다. 최신 [artifact](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36681296227/artifacts/11082290513)는 ID 11082290513, 22,317 bytes, 조회 시 expired=false입니다.

이 Cloud에서 artifact 다운로드는 HTTP 403으로 BLOCKED였습니다. 파일을 받지 못해 다운로드된 패키지 검사도 BLOCKED이며 실제 CI 결과 파일을 추가 대조했다고 설명하지 않습니다. 로컬 생성 패키지의 검증은 PASS입니다. 휴대폰 브라우저의 해당 Run에서 artifact를 받을 수 있는지는 자신의 GitHub 접근 환경에서 확인합니다.

전체 검증의 정상 종료 코드 0은 모든 검사 PASS입니다. BLOCKED/SKIPPED가 있으면 2, FAIL이 있으면 1입니다. 실제 Private Registry Root는 init하지 않으며 AWS/HCP credentials, 사용자 Terraform 설정을 격리합니다.

## 실제 입력 없어서 완료하지 않은 항목

- AWS account/VPC/Subnet/AMI/egress 및 State 저장·잠금·백업·비용 확인
- 실제 EC2/SSM 접속, AL2023 Docker/iptables 지속성, Token 런타임 주입
- 실제 HCP Organization/entitlement, Registry 게시·다운로드, Workspace/Policy Set 연결
- 실제 OIDC/IAM API 허용, 역할 output과 Workspace 등록
- 별도 AI Client→AWS MCP 연결 및 실제 Private Module 조회
- 실제 Speculative/Standard Run, HCP 정책 실패/수정, 수동 Apply 대기와 S3 결과

이 Cloud 환경에는 AWS/HCP 자격증명이나 위 실제 계정값이 제공되지 않았습니다. 준비 파일과 Mock 결과로 실제 배포/조회가 완료됐다고 판단하지 않습니다. 자세한 입력은 `required-inputs.md`, 실제 실행 순서는 `../docs/09-cloud-preparation.md`를 확인합니다.

## 로컬 후속 검증

2026-09-30 로컬 PC에서 기존 증거를 보존하는 `--reports-dir` 옵션을 추가했습니다. 단위 테스트 19개와 offline subset/ZIP 검사, 별도 Terraform fmt는 PASS입니다. Linux 전체 검증은 재실행하지 않았습니다. 상세는 progress.md의 로컬 재개 기록과 local-validation-20260930-final/validation-results.json을 확인합니다.

## AMI 환경 조건 후속 보완

2026-09-30 허용 이름 패턴 두 개와 명시적 ID/Architecture 확인을 추가했습니다. 로컬 unit 20개/사전 검사/ZIP/fmt PASS. 실제 AMI/계정/HCP 조회 및 배포는 미수행이며 외부 인증 사용이 자동 승인 검토에서 차단됐습니다. 첨부 handoff ZIP은 다운로드 도구의 접근 실패로 내부 문서를 읽지 못했습니다. 기존 Cloud 전체 결과와 새 로컬 부분 결과는 progress.md에서 구분합니다.
