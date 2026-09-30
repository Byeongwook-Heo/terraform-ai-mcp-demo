# Phase 1 진행·검증 보고

확인일: 2026-09-30 UTC. 현재 기준 경로: `/workspace/terraform-ai-mcp-demo`. **Phase 1 구현과 계정 없는 검증을 완료했으며, 외부 배포는 수행하지 않았습니다.** 초기 구현·전체 테스트는 `/workspace/terraform-mcp-demo`에서 수행했고, 후속 요청에 따라 기존 GitHub 저장소로 통합했습니다.

## 입력과 저장소 상태

첨부 ZIP의 `AGENTS.md`(4,034 bytes), `DEMO_SPEC.md`(16,310 bytes), `START_HERE.md`(3,318 bytes)를 전체 읽고 기존 내용을 보존했습니다. 접근 불가 파일은 없습니다. 초기 작업 당시 `/workspace`는 기존 Git 저장소가 아니며 기존/하위 AGENTS.md도 없었습니다. 전용 로컬 저장소와 `phase1` Branch를 만들었습니다. 당시 Git remote 및 연결된 PR 대상은 없어 새 외부 Repository/PR을 만들지 않았습니다. 이후 사용자가 지정한 기존 GitHub 저장소의 상태는 아래 후속 기록에 있습니다.

## 작성한 변경

| 경로 | 구현 |
|---|---|
| infra/mcp-host | 기존 VPC/Subnet/AMI 입력, EC2/암호화 EBS/IMDSv2 hop 1, 기본 Inbound/공인 IP 없음, SSM Profile, bootstrap |
| infra/hcp-aws-identity | 기존 OIDC 재사용 기본값, 정확한 Org/Project/Workspace/audience/run_phase, 별도 Plan/Apply Role, exact Bucket IAM |
| services/terraform-mcp | 1.3.0+digest 고정, 조회 Tool 6개, 고정 sudo stdio 런처, metadata/호스트 접근 차단, Token 런타임 파일 검사 |
| packages/terraform-aws-s3-standard | Bucket, Public Access Block, Versioning, ManagedBy, force_destroy=false, outputs |
| packages/aws-ai-demo | Registry Source/Version Root 템플릿, Owner 제거/복구 patch, 로컬 renderer |
| packages/terraform-demo-policies | hard-mandatory Owner Policy, 12개 Sentinel Mock |
| client-configs | Codex TOML, SSH over SSM, 별도 VS Code JSON, 사람/Client SSM IAM JSON 예시 |
| scripts / tests | credential-free preflight/검증, network=none Terraform plan 테스트, 런처/Token/patch 단위 테스트, offline MCP 프로토콜 Probe |
| docs / reports / CI | 한국어 운영 문서 9개, 패키지 README, 공식 근거·필요 입력, 검증 전용 CI와 결과 로그 |

전체 변경 파일은 `reports/changed-files.txt` 및 PR diff에 있습니다. 초기 구현에서는 지침 원문 3개를 변경하지 않았고, 저장소 통합 때 `AGENTS.md` 끝에 사용자 지정 저장소 지침을 추가했습니다. 기존 지침 내용과 나머지 두 파일은 보존했습니다. 네 활성 Terraform 디렉터리에 Provider lockfile을 포함했습니다. Registry 템플릿은 활성 Root에 섞지 않았습니다.

## 실제 실행한 명령과 결과

작업 도구는 격리 `/tmp/phase1-tools/`에 설치했습니다. 아래 Terraform init에는 빈 HOME/CLI config와 인증 없는 공개 download proxy만 전달했고, AWS/HCP credentials를 상속하지 않았습니다.

| 검사/명령 | 결과 | 근거 |
|---|---|---|
| unzip -l / unzip -p, 기존 지침·구조 확인 | PASS | 세 파일 전체 읽음, 원문 보존 |
| git --version / docker version | PASS | Git 2.52.0, Docker CLI+daemon 28.4.0 |
| 공식 문서 curl, 공개 Git ls-remote/clone | PASS / 일부 초기 FAIL | references.md에 성공·실패 경로 구분 |
| terraform_1.13.5 및 sentinel_0.40.0 SHA256 대조 | PASS | 공식 sums와 일치 |
| terraform fmt -recursive / fmt -check -recursive | PASS | 네 활성 Root 및 HCL 테스트/fixture |
| 디렉터리별 init -backend=false -input=false -no-color | PASS × 4 | 공개 AWS Provider 6.14.1 설치, HashiCorp 서명, Backend 사용 없음 |
| 디렉터리별 validate -no-color | PASS × 4 | Host, Identity, Module, local harness |
| Mock Provider + command=plan 사전 HCL 검사 | PASS | 10개 run 모두 aws mock, real override/apply/provisioner/외부 Root 차단 |
| network=none Docker 내 terraform test -no-color | PASS: 10/10 | Host 2, Identity 2, S3 Module 3, local harness 3; 실제 Provider API 호출 없음 |
| sentinel test -verbose | PASS: 12/12 | 정상/누락/빈 Owner/무관한 resource/순수 삭제 및 추가 edge case |
| bash -n × 6 / shellcheck --severity=warning | PASS | bootstrap, 런처, network guard, 설치/검증 스크립트 |
| Python unittest discover -s tests/unit -v | PASS: 7/7 | implicit apply/real override 거부, 런처 allowlist/argv, Token 파일, Root patch 복구 |
| Codex TOML·관련 JSON 파싱 / Secret·기본값 검사 | PASS | preflight 및 단위 테스트; 패턴 검사만으로 임의 Secret 부재를 수학적으로 보장하지 않음 |
| Python AST parse | PASS: 8개 파일 | 검증/운영/Probe 스크립트 문법 |
| docker run MCP --help / --version (network none) | PASS | stdio/--tools 및 1.3.0 확인. 이 자체를 MCP 연결 성공으로 취급하지 않음 |
| tests/mcp/probe.py --offline | PASS | 실제 공식 MCP initialize→tools/list(6)→허용 외 tools/call 거부, 계정 없는 loopback Mock API |
| git diff --check 및 원문 지침 bytes 대조 | PASS | 최종 마감 검사 로그/변경안 |
| 최종 Registry Root init/validate | BLOCKED | 실제 Source/게시/조회 권한 미제공; renderer+patch 검사만 실행 |
| 실제 AWS/HCP API, EC2/SSM/Client 연결, Private Module tools/call | BLOCKED | 실제 입력·권한과 Phase 2 승인 없음 |
| HCP Sentinel entitlement/Policy Set/Override 연동 | BLOCKED | 계약/실제 Organization 미확인 |
| 실제 계정 plan / apply / destroy / import / 통합 test | SKIPPED | 이번 요청에서 금지. 실제 State 변경 없음 |
| 초기 GitHub PR 및 원격 CI 실행 | BLOCKED | 초기 구현 시 remote 없음. 후속 저장소 지정 요청으로 게시 작업 진행; 아래 결과 참조 |

자동 검증 entrypoint: `PATH=/tmp/phase1-tools/venv/bin:/tmp/phase1-tools:$PATH bash scripts/validate-phase1.sh`. 개별 명령의 계정 없는 로그는 `reports/validation-logs/`, 기계 판독 결과는 `reports/validation-results.json`에 있습니다. 별도 보완 검사도 `reports/final-checks.json`에 기록합니다.

## 발견한 실패와 해결

1. GitHub API 403/raw URL 404 → 공개 tag clone/release/Image로 대조했습니다. 계정 Token을 요청하지 않았습니다.
2. proxy 없는 초기 init 연결 거부 → 인증 정보가 없는 proxy만 허용하고 격리된 빈 HOME에서 성공했습니다.
3. Sentinel JSON multiline Mock의 쉼표 문법과 string type 비교 오류 → Sentinel 문법 및 types.type_of로 수정하고 12개 테스트를 재실행해 통과했습니다.
4. Python target install 경로가 fresh subprocess에 전달되지 않음 → 별도 venv로 실행해 7개 단위 테스트가 통과했습니다.
5. capability를 제거한 Docker root가 host uid 소유 0700 임시 디렉터리에 접근하지 못함 → 컨테이너 uid/gid를 작업 사용자와 일치시켜 격리된 10개 Mock Plan이 통과했습니다.
6. Token 없는 MCP는 HCP Tool을 등록하지 않음 → network=none loopback의 ping 전용 API Mock과 비자격증명 fixture 문자열을 사용했습니다. API client 등록 완료 후 tools/list를 확인합니다. 실제 계정 조회는 없습니다.
7. Terraform runtime의 BusyBox에 httpd applet이 없음 → 고정 Python runtime과 표준 라이브러리 Mock을 사용합니다. 초기 실패를 실제 MCP 성공으로 기록하지 않았습니다.

8. git diff --check가 validate 로그의 마지막 빈 줄을 지적함 → 로그 끝의 빈 줄을 정규화하고 마감 검사를 다시 수행했습니다.

9. 다운로드 묶음의 기본 `/mnt/data` 경로에 쓰기 권한이 없음 → 쓰기 가능한 `/workspace/phase1-artifacts`에 ZIP/diff/보고서를 만들었습니다.

최종 자동 검증에는 FAIL이 없습니다. Mock 통과는 AWS IAM/배포, 실제 Private Registry/HCP Policy 성공과 별개입니다.

## 남은 작업과 승인 경계

실제 AL2023 bootstrap, Docker/iptables 지속성·metadata 차단, 전용 OS 계정/sshd/sudoers, SSM 모바일 연결, HCP Token 권한, OIDC claim/IAM API, Registry 게시·Module 다운로드, 실제 Client MCP 조회, Policy Set/Override와 Standard Run 승인 대기는 검증하지 않았습니다. Phase 2의 입력과 승인 범위는 `required-inputs.md`를 확인하세요.

Token은 /run의 Root 파일과 런타임 환경으로만 전달하도록 작성했지만 호스트 root/Docker 관리자는 이를 읽을 수 있습니다. 관리자와 시연 Client를 분리하고 발급·회수·로그 경계를 확인해야 합니다. 인증 없는 HTTP MCP나 공개 SSH, s3:* 및 자동 배포 CI는 작성하지 않았습니다.

초기 납품물은 `terraform-mcp-phase1.zip`, `terraform-mcp-phase1.patch`, `phase1-review.md`였습니다. ZIP에는 코드·문서·검증 로그만 포함하고 .git/.terraform/cache/State는 제외했습니다. 당시 로컬 Branch는 phase1이며 변경 파일 127개를 staged diff로 남겼습니다. 현재 작업 Branch와 GitHub 검토 경로는 후속 기록 및 `repository.md`를 확인하세요.

검토 후 자동으로 Phase 2를 시작하지 않습니다. 검토 가능한 코드, lockfile, Mock 결과, 한국어 문서, diff/ZIP만 남깁니다.

## 후속 요청: PC 없이 할 작업 정리

`docs/08-without-pc.md`에 휴대폰에서 가능한 작업의 추천 순서, 외부 변경 승인 경계, 별도 시연 Client 조건과 비민감 입력 메모를 추가했습니다. README에서 연결하고 ZIP/diff/보고서 묶음을 갱신했습니다. 실제 계정 연결이나 배포는 수행하지 않았습니다.

문서의 로컬 링크와 git diff --check를 확인했습니다. 실행 코드가 변경되지 않아 기존 Phase 1 테스트 결과를 유지했으며 Terraform/Mock 테스트를 재실행하지 않았습니다.

## 후속 요청: GitHub 기준 저장소 지정·통합

사용자가 `terraform-ai-mcp-demo`를 지정하고 앞으로 해당 저장소에서 작업하도록 요청했습니다. GitHub 연결에서 기존 Private 저장소 `Byeongwook-Heo/terraform-ai-mcp-demo`와 접근 권한을 확인했습니다. main은 `53b0f820bbfb99fd447a827f652b29db27d19361`이며 README만 있었습니다. 저장소를 clone하여 기존 이력을 유지하고 `codex/phase1-terraform-mcp` Branch를 만들었습니다. 새 Repository는 생성하지 않았습니다.

Phase 1 추적 파일만 복사하고 .git/cache/State/자격증명은 제외했습니다. 기존 README 제목을 유지하여 프로젝트 설명과 검토 안내를 통합했습니다. `AGENTS.md` 기존 내용 뒤에 기준 저장소 지침을 추가하고, `reports/repository.md`, 휴대폰 체크리스트와 필요 입력 목록을 갱신했습니다.

새 저장소에서 `preflight(root)`, `static_checks(root)`, Python AST/상대 링크 검사, `python -m unittest discover -s tests/unit -v`, `terraform fmt -check -recursive .`, `git diff --check`를 수행했습니다. 정적 검사와 단위 테스트 7개는 PASS이며 기존 파일 125개의 byte가 초기 검증본과 일치했습니다. 이 중 실행 코드·Terraform·Sentinel·CI는 변경하지 않았습니다. `AGENTS.md` 기존 원문이 추가 지침 앞에 그대로 남아 있는지도 확인했습니다. 이번 통합 검사 결과는 `repository-checks.json`과 `*-repository-check.txt`에 있습니다.

GitHub Actions 설정의 읽기 API는 integration 권한 부족으로 HTTP 403(BLOCKED)을 반환했습니다. 저장소 설정 변경이나 Workflow dispatch를 시도하지 않았으며, 기존 검증 CI 파일만 포함합니다. 이전 전체 검증과 이번 저장소 통합 검사를 구분합니다. Branch Push 및 Draft PR의 실제 결과는 이 절과 `repository.md`에 이어서 기록합니다. 실제 AWS/HCP 연결, Module 게시, PR Merge, Tag 게시, 배포 Workflow는 수행하지 않습니다.
