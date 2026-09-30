# 작업 진행·검증 기록

2026-09-30 KST 최신 상태: **AWS 기반 인프라 생성·검증 PASS, HCP Workspace 미생성**입니다. 사용자 AWS 생성 승인 후 Host 6개/Identity 5개를 새 S3 backend Plan으로 Apply했고, 전용 State Bucket 1개는 별도 bootstrap으로 생성했습니다. 배포 후 두 실제 Plan은 변경 없음(exit 0), EC2 running/상태 검사 ok/SSM Online을 재확인했습니다.

실제 EC2의 MCP 고정 Image·Mock 프로토콜, SSH over SSM 공개키 인증·host key 검사, HCP 공개 TLS ping·IMDS 차단은 PASS입니다. 최초 SSH 실패의 공개 authorized_keys 권한을 Root 0600→0644로 수정하고 재검증했습니다. 최소 조회 Token은 주입하지 않았으며 실제 Private Registry/AI Client 시연은 남았습니다.

HCP 예정 Workspace GET 3개는 404이며 POST/PATCH/DELETE는 수행하지 않았습니다. 기존 HCP Local State 제안 대신 실제 State는 암호화·버전 관리·native lockfile을 적용한 S3에 있습니다. [실제 생성 후 재개 안내](../docs/11-aws-created.md)와 [비식별 실행 증거](aws-deployment-20260930.json)를 기준으로 이어갑니다. 이전 Cloud/CI 증거는 보존했고 설치 코드 수정의 새 credential-free CI는 게시 후 확인합니다.

## 이전 준비·검증 기록

최신 구현 Commit 2ddc772의 [CI Run 36693140577](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36693140577)도 전체 29개 PASS입니다. 다운로드 artifact에서 Python 24개/Mock Plan 14개/Sentinel 12개와 ZIP 재검사를 대조해 operator-ci-evidence-20260930에 별도로 보존했습니다. 최종 후속 Commit은 보고서와 문서 EOF 정리만 포함하며 실행 코드 변경은 없습니다.


최신 상태: 2026-09-30 운영 기본값 선택을 위임받아 기존 Private Subnet/허용 AL2023 AMI/HCP Local State/Owner·Bucket 이름을 준비했습니다. 실제 계정의 Host 6개/Identity 5개 신규 Plan(init/validate 포함) PASS, 수정·삭제 0개. Python 24개/ZIP/정적 검사 PASS. AWS/HCP 생성·Apply·MCP 실연결은 미수행이며 구체적인 첫 생성 범위만 승인 대기입니다. operator-preparation-20260930.json과 docs/10-operator-state-and-review.md를 확인합니다. 아래 기록은 해당 시점의 이력입니다.


## 현재 작업 기준 — 최신 main

최신 상태: 2026-09-30 17:20 KST 사용자 승인 후 AWS STS·EC2 AMI와 HCP 조직 GET 실제 조회/재대조 PASS. 재첨부 ZIP의 3개 지침을 읽었으며 ZIP에 없는 2개 보고서는 main에서 읽었습니다. 실제 변경은 미수행입니다. 상세는 마지막 읽기 전용 조회 기록과 read-only-discovery-20260930.json을 확인합니다. 아래 이전 BLOCKED는 각 작업 당시 기록입니다.

2026-09-30 로컬 후속 작업: AMI 두 이름 패턴 검증과 OS 확인을 추가했습니다. 20개 단위 테스트/사전 검사/게시 ZIP 검사/형식 검사 PASS. 새 Linux CI Run 36688256340은 29개 검사 PASS이며 다운로드 artifact도 대조했습니다. AWS/HCP 외부 인증 조회와 첨부 ZIP 읽기는 BLOCKED이며 상세는 마지막 AMI 보완 기록을 확인합니다. 직전 Commit 425d527의 Linux CI는 Run 36686103804 completed/success입니다.

사용자의 최신 지시는 **이 준비 저장소의 main에서 직접 작업하고 Phase 번호와 관계없이 가능한 Cloud 구현·검증을 이어가는 것**입니다. 새 채팅의 변경을 원격 main에서 확인했으며 Phase 1 PR #1은 이미 병합됐습니다. 앞선 Branch/Draft PR 안내는 과거 상태입니다. 실제 AWS/HCP 입력과 접근 환경이 필요한 항목은 `required-inputs.md`에서 관리합니다.

새 채팅에서 게시 패키지·입력 생성기, Mock MCP 검색/상세, 정상/실패/복구 정책 리허설을 추가했고 전체 검사 28개 및 [원격 CI Run 36679127805](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36679127805)가 PASS입니다. 이번 후속 보완에서는 ZIP 다운로드 후 무결성·내용 검증기를 추가했고 최신 로컬 검사 29개와 단위 테스트 17개가 PASS입니다. 최신 결과와 완료 범위는 `cloud-completion.md`, `cloud-validation-summary.json`, `validation-results.json`을 확인하세요.

최신 보완도 main에 직접 게시했고 [CI Run 36681296227](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36681296227)가 PASS입니다. Cloud의 artifact 다운로드는 HTTP 403으로 BLOCKED이며 로컬 ZIP 검사·CI 성공과 구분합니다. 최신 게시 확인은 `main-continuation.json`에 있습니다.

**아래 기록은 작업 당시의 상태를 보존한 이력입니다.** 초기 BLOCKED/SKIPPED, main 미변경 및 미Merge 기록을 현재 상태로 해석하지 않습니다.

## 초기 Phase 1 기록

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
| 후속 작업 Branch 게시 / Draft PR | PASS | 기존 terraform-ai-mcp-demo에 Branch와 PR #1 생성, main 미변경 / 미Merge |
| 초기 원격 검증 CI | SKIPPED | 당시 Workflow Run 0개; 이후 성공한 Run은 최신 완료 보고 참조 |

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

초기 Phase 1 요청은 검토 가능한 코드, lockfile, Mock 결과, 한국어 문서, diff/ZIP을 남기고 종료하는 범위였습니다. 이후 main에서 가능한 Cloud 작업 전체를 이어가는 사용자 지시로 갱신됐습니다.

## 후속 요청: PC 없이 할 작업 정리

`docs/08-without-pc.md`에 휴대폰에서 가능한 작업의 추천 순서, 외부 변경 승인 경계, 별도 시연 Client 조건과 비민감 입력 메모를 추가했습니다. README에서 연결하고 ZIP/diff/보고서 묶음을 갱신했습니다. 실제 계정 연결이나 배포는 수행하지 않았습니다.

문서의 로컬 링크와 git diff --check를 확인했습니다. 실행 코드가 변경되지 않아 기존 Phase 1 테스트 결과를 유지했으며 Terraform/Mock 테스트를 재실행하지 않았습니다.

## 후속 요청: GitHub 기준 저장소 지정·통합

사용자가 `terraform-ai-mcp-demo`를 지정하고 앞으로 해당 저장소에서 작업하도록 요청했습니다. GitHub 연결에서 기존 Private 저장소 `Byeongwook-Heo/terraform-ai-mcp-demo`와 접근 권한을 확인했습니다. main은 `53b0f820bbfb99fd447a827f652b29db27d19361`이며 README만 있었습니다. 저장소를 clone하여 기존 이력을 유지하고 `codex/phase1-terraform-mcp` Branch를 만들었습니다. 새 Repository는 생성하지 않았습니다.

Phase 1 추적 파일만 복사하고 .git/cache/State/자격증명은 제외했습니다. 기존 README 제목을 유지하여 프로젝트 설명과 검토 안내를 통합했습니다. `AGENTS.md` 기존 내용 뒤에 기준 저장소 지침을 추가하고, `reports/repository.md`, 휴대폰 체크리스트와 필요 입력 목록을 갱신했습니다.

새 저장소에서 `preflight(root)`, `static_checks(root)`, Python AST/상대 링크 검사, `python -m unittest discover -s tests/unit -v`, `terraform fmt -check -recursive .`, `git diff --check`를 수행했습니다. 정적 검사와 단위 테스트 7개는 PASS이며 기존 파일 125개의 byte가 초기 검증본과 일치했습니다. 이 중 실행 코드·Terraform·Sentinel·CI는 변경하지 않았습니다. `AGENTS.md` 기존 원문이 추가 지침 앞에 그대로 남아 있는지도 확인했습니다. 이번 통합 검사 결과는 `repository-checks.json`과 `*-repository-check.txt`에 있습니다.

GitHub Actions 설정의 읽기 API는 integration 권한 부족으로 HTTP 403(BLOCKED)을 반환했습니다. 저장소 설정 변경이나 Workflow dispatch를 시도하지 않았으며, 기존 검증 CI 파일만 포함합니다. 원격 Run 목록 조회는 성공했지만 Run이 0개여서 원격 CI 검증은 SKIPPED로 기록했습니다. 이전 전체 검증과 이번 저장소 통합 검사를 구분합니다.

`git push -u origin codex/phase1-terraform-mcp`는 HTTP 401로 FAIL했습니다. 이후 연결된 GitHub 앱의 create_branch → create_tree → create_commit → update_ref(force=false)로 게시했습니다. 로컬·원격 Git tree가 `87d53359283d72094f007084ccde5a3df7b5657c`로 일치했고 `git diff --exit-code HEAD origin/codex/phase1-terraform-mcp`가 PASS했습니다. 원격 구현 Commit은 `5f3ecfcea93bf369fa08437038add7be253bbb0a`입니다. fetch 후 같은 작업 Branch를 원격 Commit에 맞추고 upstream을 설정했습니다.

앱의 create_pull_request는 Internal error로 FAIL하여 Open PR이 없음을 먼저 조회했습니다. 이후 `gh pr create --repo Byeongwook-Heo/terraform-ai-mcp-demo --head codex/phase1-terraform-mcp --base main --draft --title … --body-file /tmp/terraform-ai-mcp-phase1-pr.md`로 **[Draft PR #1](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/pull/1)**을 생성했습니다. `gh api …/pulls/1`로 Open/Draft, 정확한 base/head, merged=false를 확인했습니다. 원격 main은 기존 SHA 그대로입니다. 게시 결과와 실패 후 대체 경로는 `github-publication.json`, 저장소 재개 방법은 `repository.md`에 기록했습니다.

실제 AWS/HCP 연결, Module 게시, PR Merge, Tag 게시, 배포 Workflow는 수행하지 않았습니다. 저장소 통합과 Phase 1 검토 가능한 변경안을 남기는 것으로 이번 작업을 종료합니다.

## 후속 요청: main에 Cloud 준비 전체 반영 — 2026-09-30

사용자가 작업 Branch에만 남기지 않고 main에 두며 Phase 2 이후의 Cloud 작업까지 진행하도록 요청했습니다. 시작 시 main은 Phase 1 PR #1의 병합 Commit `f7299c10fa1b9376988644d85983d6e24f5add70`이었고 저장소는 Public입니다. 기존 main 이력을 보존하고 새 작업 Branch 없이 main에서 작업했습니다. 기존 infra/Module/Policy/운영 런처는 변경하지 않았습니다.

추가한 주요 파일은 `configs/demo-inputs.example.json`, `scripts/demo_preparation.py`, `scripts/prepare-demo.py`, `scripts/rehearse-demo.py`, `scripts/secret_patterns.py`, `tests/unit/test_preparation.py`, `docs/09-cloud-preparation.md`, `reports/cloud-completion.md`입니다. MCP Mock API/Probe는 실제 고정 Image에서 Module 검색과 상세 조회까지 검증하도록 확장했습니다. README/START_HERE/AGENTS/휴대폰 안내/저장소 기록을 main 기준으로 갱신하고 CI의 main push 검증과 artifact 보존을 추가했습니다.

실행: `bash scripts/install-validation-tools.sh`(GITHUB_PATH로 설치 PATH 기록) → 설치 도구 PATH에서 `bash scripts/validate-phase1.sh`. Terraform/Sentinel 공식 SHA256, ShellCheck 고정 SHA256 대조는 PASS입니다. 최종 전체 종료 코드 0, 검사 28개 모두 PASS입니다. Python 12개, Terraform Mock Plan 10개, Sentinel Mock 12개와 리허설 3개를 확인했습니다. MCP initialize/tools/list(6), 허용 외 쓰기 도구 거부, Mock Private Module 검색/상세/Version/Input/Output 호출이 PASS입니다. 세부 결과는 `validation-results.json`, `validation-logs/`, `rehearsal.json`, `cloud-validation-summary.json`입니다.

`python scripts/prepare-demo.py --config configs/demo-inputs.example.json --output .artifacts/prepared`로 게시 ZIP 3개와 SHA256을 실제 생성했습니다. State/Secret/임의 파일과 symlink가 게시 패키지에 포함되지 않는 검사, 같은 입력의 SHA256 재현성, 기존 출력 덮어쓰기 거부, 완전한 fixture 입력에서 Root/Role/Workspace/Client 파일 생성과 Owner patch 복구를 확인했습니다. 현재 실제 입력은 미정이라 계정별 파일 생성은 BLOCKED이며 `cloud-preparation-readiness.json`에 기록합니다.

실제 AWS/HCP 자격증명이나 계정값은 이 Cloud 환경에 제공되지 않았습니다. AWS 리소스 생성, HCP Registry/Workspace/Policy Set 변경, 실제 Module 조회, 시연 Run/Apply/정리는 수행하지 않았습니다. 패키지와 Mock 성공을 실환경 성공으로 설명하지 않습니다. 원격 CI 상태는 아래 게시 확인 기록에서 로컬 검사와 구분합니다.

### main 게시 확인: BLOCKED

검증한 코드 Commit은 `07f96d0b4f387c37ad62546cf1daa3f1e863e1e3`이며 tree와 원격 상태를 `cloud-publication.json`에 기록합니다. `git push`는 HTTP 403, 연결 앱의 create_tree와 실제 준비 파일 create_blob도 HTTP 403(Resource not accessible by integration)으로 실패했습니다. 원격 main은 Phase 1 병합 Commit 그대로이며 force/update_ref를 호출하지 않았습니다.

GitHub user/installations 조회에서 `chatgpt-codex-connector`의 contents/workflows/actions가 write이고 repository_selection=all임을 확인했습니다. 그러나 installation 110044473이 suspended_at=2026-09-30T04:54:26Z로 일시 중지되어 있습니다. 연결 복구를 사용자에게 안내하고 코드·검증·게시 패키지·Git patch를 보존했습니다. 현재 원격 CI는 SKIPPED: 새 코드를 게시할 수 없어 새 workflow Run의 성공을 확인할 수 없습니다.

## GitHub 연결 복구와 main 게시 재개 — 2026-09-30T15:32:47+09:00

GitHub 인증 계정 Byeongwook-Heo, 설치 110044473의 suspended_at=null과 contents/workflows/actions write를 확인했습니다. 원격 main은 기존 Phase 1 Commit 그대로였습니다. 일반 Git Push는 HTTP 401 전송 오류로 실패했고, API/ls-remote로 원격이 변경되지 않았음을 확인했습니다. 실제 준비 파일의 create_blob은 PASS입니다. 이전 403 차단은 해제됐으며 검증한 코드의 Git Data API 게시를 재개합니다. 코드 변경 없이 기존 전체 28개 PASS 결과를 유지합니다.

### main 게시 성공 — 2026-09-30T15:39:04+09:00

create_tree → create_commit → update_ref(force=false)가 모두 PASS입니다. GitHub tree `2d3fcf29c65579024aedc6cc68ec1c3de7160719`가 검토한 로컬 main tree와 일치했고 원격 main은 구현 Commit `faf4b2ce11222d3546306be1dabfdbf09a9b20e3`로 갱신됐습니다. fetch 후 git diff --exit-code HEAD origin/main이 PASS입니다. 같은 파일 tree임을 확인한 뒤 git reset --soft origin/main으로 작업 main도 원격에 맞췄습니다. 새로운 작업 Branch를 만들지 않았습니다.

main 게시 직후 자동 Run이 없어 active workflow를 workflow_dispatch로 실행했습니다. 검증 Run은 36679127805이며 실제 conclusion을 확인한 뒤 최종 상태를 기록합니다. 원격 CI와 이전 로컬 검증을 구분합니다. AWS/HCP 실환경 자격증명이나 계정값은 여전히 제공되지 않아 실제 리소스 변경은 수행하지 않습니다.

### GitHub Actions 검증 성공

[Run 36679127805](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36679127805)의 status=completed, conclusion=success와 head_sha=`faf4b2ce11222d3546306be1dabfdbf09a9b20e3`를 API 및 gh run watch --exit-status(종료 코드 0)로 확인했습니다. validate Job과 도구 설치/전체 검증/게시 패키지 생성/증거 업로드 Step이 모두 success입니다. artifact `cloud-preparation-faf4b2ce11222d3546306be1dabfdbf09a9b20e3`(ID 11080114938, 21465 bytes, expired=false)를 확인했습니다.

게시·완료·저장소·진행 보고서 4개만 최종 상태로 갱신했습니다. 실행 코드 변경이 없으므로 통과한 전체 검증을 유지하고 JSON 파싱/정적 검사/git diff --check를 수행합니다. GitHub main 게시를 보고서까지 마무리하며 실제 AWS/HCP 변경은 수행하지 않습니다.

## main에서 이어서 보완 — 2026-09-30 KST

새 채팅에서 바뀐 원격 main `d4aae85`와 지침을 확인하고 작업 디렉터리의 main을 fast-forward했습니다. 저장소의 Public 상태, PR #1 병합과 이전 CI Run 36679127805의 completed/success를 실제 GitHub API로 확인했습니다. 새 작업 Branch는 만들지 않았습니다.

추가 파일은 `scripts/publication_verification.py`, `scripts/verify-prepared-demo.py`, `tests/unit/test_publication_verification.py`입니다. ZIP 3개·checksum·readiness의 일관성, 필수 파일, 비허용 경로/State/중복 파일명/symlink/암호화/크기/Secret 패턴을 검사합니다. ZIP을 압축 해제하거나 외부 API/Terraform 명령을 호출하지 않습니다. checksum은 서명이 아니며 승인된 CI Commit과 대조해야 한다는 한계를 문서화했습니다.

`env -i … python -m unittest discover -s tests/unit -v`가 PASS(17개)였고, `PATH=/tmp/phase1-tools/venv/bin:/tmp/phase1-tools:$PATH bash scripts/validate-phase1.sh`는 종료 코드 0, 전체 검사 29개 PASS입니다. Terraform 사전 검사로 aws Mock/명시적 command=plan run 10개를 확인한 뒤 network=none 테스트를 실행했습니다. Sentinel Mock 12개와 정상/실패/수정 리허설 3개, MCP Mock Module 조회가 모두 통과했습니다. 검사 로그는 `validation-logs/publication-verification.txt` 및 전체 결과 파일에 있습니다. 기존 Module/Root/Policy 패키지 SHA256은 바뀌지 않았습니다.

README/START_HERE/휴대폰 안내에 생성·다운로드 후 검사 명령을 추가했습니다. 진행 보고서 첫 화면에 최신 main 기준을 두고 옛 Branch/CI BLOCKED 기록을 이력으로 명시했습니다. 실제 입력 문서 제목에서도 Phase 2 한정 표현을 제거했습니다. 새 실행 코드의 원격 CI는 main 게시 후 확인합니다. 실제 AWS/HCP 연결·리소스 변경은 수행하지 않았습니다.

마감 보완 검사에서 시스템 python3를 사용해 hcl2 모듈을 찾지 못한 FAIL이 있었습니다. 설치된 `/tmp/phase1-tools/venv/bin/python`으로 다시 실행해 정적 JSON/TOML/HCL/Secret 검사, Python AST 16개, 문서 링크가 PASS임을 확인했습니다. 전체 검증은 처음부터 해당 venv에서 실행했으며 29개 PASS 결과와 별개인 마감 명령 오류입니다.

### 이번 main 게시와 원격 검증

Git Data API로 create_tree → create_commit → update_ref(main, force=false)를 실행해 Commit `fbb9bcc6e94c708c5300f1cd6366326727f5ac97`를 게시했습니다. 검증한 tree `67c70f3860b33cfa5511db192031a575ada4e9a6`와 원격 파일이 일치했고 fetch 후 `git diff --exit-code HEAD origin/main`이 PASS했습니다. 같은 파일임을 확인한 뒤 로컬 main의 Commit도 원격에 맞췄습니다. 기존 main 이력을 보존했습니다.

해당 SHA의 자동 Run이 없어 검증 전용 `gh workflow run phase1-validation.yml --ref main`을 실행했습니다. Run 36681296227의 completed/success 및 정확한 head SHA와 Job/Step 성공을 API로 확인했고 `gh run watch --exit-status`도 종료 코드 0입니다. artifact ID/크기/expired=false를 확인했습니다. 기존 upload-artifact Action의 Node.js 20→24 강제 실행 annotation은 있었지만 모든 Step이 성공했습니다. Action 버전을 임의로 바꾸지 않았습니다.

`gh run download`는 Cloud 다운로드 endpoint의 HTTP 403으로 FAIL했으며 다운로드된 파일이 없습니다. 그 디렉터리의 ZIP 검증 명령도 필요한 파일이 없어 실패했습니다. 다운로드 파일 검사는 BLOCKED로 남기며 CI 성공이나 로컬 ZIP PASS와 혼동하지 않습니다. 오류 원문의 임시 서명 URL은 보고서·Git에 저장하지 않습니다. 게시·CI 결과를 문서와 JSON에 반영하는 후속 Commit은 실행 코드 변경이 없어 전체 테스트를 반복하지 않고 정적 검사·diff·원격 파일 일치를 확인합니다.

## 로컬 PC에서 main 재개 — 2026-09-30 KST

기준 Commit `44e77c6`. 지정 문서 AGENTS.md, DEMO_SPEC.md, START_HERE.md, cloud-completion.md, progress.md를 확인했습니다. 기존 Cloud 보고서와 로그는 보존했습니다.

변경: `scripts/validate-phase1.py`에 `--reports-dir`를 추가하고 Shell wrapper에서 인수를 전달합니다. 지정 경로가 존재하면 종료 코드 2로 거부해 기존 증거를 덮어쓰지 않습니다. 기본 CI 경로와 실행은 유지됩니다. `tests/unit/test_validation_output.py`는 기존 증거 보존 및 --live 거부를 확인합니다.

검증: Python 3.14 임시 venv에 requirements-validation.txt 고정 의존성을 설치했습니다. `python -m unittest discover -s tests/unit -v` PASS 19개. 제한 PATH(venv:/usr/bin:/bin)에서 `bash scripts/validate-phase1.sh --reports-dir reports/local-validation-20260930-final` 실행: 사전 검사/10개 Mock plan 선언 확인, Shell 문법 6개, Python 19개, 게시 ZIP 생성/검사 PASS. 전체 종료 코드 2는 선택한 offline subset PATH에서 Terraform/Sentinel/ShellCheck/Docker를 제외했기 때문입니다. 설치된 Terraform 1.14.3 darwin_arm64의 `terraform fmt -check -recursive .`는 별도 PASS입니다. 고정 1.13.5 Linux Docker Mock Plan, Sentinel, MCP 프로토콜 및 init/validate는 이번 로컬 작업에서 SKIPPED이며 기존 Cloud PASS를 재실행 결과로 주장하지 않습니다.

실제 AWS/HCP 변경 및 API 연결은 미수행(BLOCKED: 대상/입력/승인 미확인). 다음 단계는 Linux CI 전체 검증과 required-inputs.md의 비민감 환경값 확인입니다. Secret 값을 채팅이나 Git에 기록하지 않습니다.

## 사용자 AWS AMI 제약 반영 및 첨부 인수인계 확인 — 2026-09-30 KST

사용자가 다운로드 폴더의 AWS credentials/HCP token 파일과 허용 AMI 이름 패턴 `hc-base-*`, `hc-security-base-*`를 지정했습니다. 파일 존재 및 필요한 field 형식만 확인했고 비밀값은 출력·보고서·Git에 넣지 않았습니다. STS 계정, EC2 AMI와 HCP Organization 읽기 전용 조회를 계획했으나 자동 승인 검토가 외부 인증 전송 승인 미확인으로 실행 전에 거부했습니다. 실제 AWS/HCP 조회/변경은 수행하지 않았습니다.

추가 첨부 `terraform-mcp-codex-handoff.zip`의 다운로드는 도구가 file ID를 authorized/resolved 할 수 없다는 오류로 BLOCKED였습니다. 로컬 Downloads와 프로젝트 sources에도 파일이 없어 내부의 지정 문서 5개는 읽지 못했습니다. 파일 내용을 추측하지 않았고, 기존 main의 지정 문서와 직접 전달된 AMI 제약만 사용했습니다. 첨부 ZIP의 지침 비교는 파일 접근 복구 뒤 진행합니다.

변경 파일: `infra/mcp-host/main.tf`의 단일 ID metadata 조회와 이름/architecture/EBS/HVM/available 필터, EC2 lifecycle precondition; `variables.tf`, `terraform.tfvars.example`; `bootstrap.sh`의 AL2023 선확인; `tests/security.tftest.hcl`의 허용 security-base/미허용 이름/arm64/다른 ID Mock 검사 4개. `scripts/safety_checks.py`는 이 AMI datasource와 literal mock override만 허용하며 다른 datasource/alias/실 Provider/묵시적 Apply는 계속 차단합니다. `tests/unit/test_safety.py`에 AMI 필터 완화와 미승인 datasource/override 거부를 추가했습니다. AGENTS/DEMO_SPEC에 사용자 환경 조건을 추가하고 AWS 준비/필요 입력/근거 문서를 갱신했습니다.

실행 결과: Python 3.14 격리 venv에서 단위 테스트 20개 PASS; Terraform 1.14.3 darwin_arm64 fmt-check와 git diff --check PASS. 제한 PATH에서 `bash scripts/validate-phase1.sh --reports-dir reports/ami-validation-20260930` 실행: 14개 run 사전 검사, Shell 문법 6개, 단위 테스트 20개와 ZIP 생성/검사 PASS. 이 로컬 subset 종료 코드 2는 PATH에서 전체 검증 도구를 제외한 SKIPPED이며 FAIL은 없습니다. 기존 reports/validation-results.json 및 Cloud 증거는 덮어쓰지 않았습니다. 새 Terraform 1.13.5/AWS 6.14.1 Docker Mock Plan과 Sentinel/MCP 검사는 게시 후 Linux CI에서 확인합니다.

미검증: 실제 AMI 후보의 ID/Owner/OS/SSM 및 네트워크, 계정의 실제 SCP/Allowed AMIs 정책, HCP 접근 권한. 이름 필터와 Mock PASS는 실제 정책·AMI 부팅 성공이 아닙니다. Apply/Destroy/계정 설정 변경은 전혀 수행하지 않았습니다.

### AMI 보완 main 게시·Linux 검증·다운로드 증거

구현 Commit `c404c346f8dc399f42706064aea0db6c0c588793`를 기존 main 이력 위에 직접 게시했습니다. [Run 36688256340](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36688256340)의 정확한 head SHA/completed/success와 Job/Step 성공을 API로 확인하고 gh run watch --exit-status도 종료 코드 0입니다.

이번 로컬에서는 gh run download가 종료 코드 0으로 artifact를 받았습니다. `validation-results.json` 29개 전부 PASS, Python 20개, Host Mock Plan 6개/Identity 2개/Module 3개/local harness 3개로 총 14개가 통과했습니다. Sentinel Mock 12개와 MCP Mock 조회도 전체 PASS에 포함됩니다. 다운로드한 ZIP 3개는 verify-prepared-demo.py로 다시 검사하여 PASS입니다. `ami-ci-20260930.json`과 `ami-ci-evidence-20260930/`에 원격 결과를 별도로 보존합니다. 이전 Cloud의 다른 Run 다운로드 403 기록을 삭제하거나 그 결과로 재해석하지 않습니다.

최종 후속 변경은 README의 현재 Mock 수와 상태·증거 보고서뿐입니다. 실행 코드를 추가로 바꾸지 않아 통과한 CI를 유지하고 JSON/Secret 정적 검사와 git diff --check를 수행합니다. 실제 AWS/HCP 조회·변경과 첨부 ZIP 문서 대조는 계속 BLOCKED입니다.

## ZIP 인수인계 확인·승인된 실제 읽기 전용 조회 — 2026-09-30 KST

사용자가 ZIP을 재첨부하고 다운로드 폴더 자격증명을 서울 리전 STS/EC2 계정·AMI 조회 및 app.terraform.io 조직 GET에 사용하는 것을 명시적으로 승인했습니다. 이전 외부 인증 전송 차단과 별개인 새 승인으로 조회를 진행했습니다. 쓰기/배포 승인은 포함되지 않습니다.

재첨부 ZIP의 일반 download_file은 다시 resolve/authorization 오류를 반환했습니다. 파일 도구의 사용자 제공 file ID에 대한 materialize 전송이 성공하여 그 정확한 첨부를 읽었습니다. ZIP SHA256은 read-only-discovery-20260930.json에 있습니다. ZIP에는 AGENTS.md(4,034 bytes), DEMO_SPEC.md(16,310 bytes), START_HERE.md(3,318 bytes)만 있습니다. reports/cloud-completion.md와 reports/progress.md는 ZIP에 없으며 현재 main의 해당 보고서를 읽었습니다. 초기 Phase 1 지침으로 대조했고, 이후 사용자 main 작업·실조회 승인과 기존 구현/증거를 되돌리거나 덮어쓰지 않았습니다.

실제 조회: `aws sts get-caller-identity --region ap-northeast-2` PASS; `aws ec2 describe-images --executable-users self` + 허용 Name/Architecture/State/EBS/HVM 필터 PASS. 일치하는 AMI 867개 중 AL2023 이름 후보 37개가 있습니다. 현재 bootstrap과 호환 가능한 단일 AL2023 x86_64 후보를 제안하고 `describe-images --image-ids`로 ID/Name/Owner/Architecture/State를 재대조해 PASS입니다. 계정도 두 번째 STS 호출로 대조했습니다. 실제 AMI 부팅/SSM/패키지/조직 이미지 정책 적합성은 아직 검증하지 않았습니다.

HCP는 사용자 Token 파일을 메모리에서만 파싱하여 GET /organizations 및 GET /organizations/{확인된 조직}로 접근과 단일 조직의 일치를 확인했습니다(PASS). 파일 내 두 Token의 조직 권한 응답은 서로 다릅니다. Token을 MCP에 주입하거나 최소권한으로 간주하지 않았습니다. plan identifier와 can-update-sentinel 응답만으로 Sentinel entitlement/강제정책 사용 가능성을 판정하지 않았으며 별도 entitlement 조회는 수행하지 않았습니다. 실제 account/AMI Owner/organization 식별자와 전체 조회 응답은 Git에서 제외된 로컬 입력·artifact에만 보존하고 공개 보고서는 비식별 요약만 포함합니다.

`configs/demo-inputs.local.json`에 검증한 Account/Organization만 기록했습니다. 후보 AMI는 승인된 배포 ID로 자동 지정하지 않았으며 ami_id는 null입니다. VPC/Subnet/Owner/Bucket/OIDC/State 등도 미정으로 유지했습니다. `python scripts/prepare-demo.py --config configs/demo-inputs.local.json --output .artifacts/discovered-preparation-20260930`으로 조직별 Root 파일과 게시 ZIP 3개 생성 PASS; `verify-prepared-demo.py` SHA256/내용 검사 PASS. mcp-host/Identity/Workspace/Client 입력은 계속 BLOCKED입니다. 이 결과는 파일 준비이며 Registry 게시·연결 성공이 아닙니다.

이번 변경은 보고서 상태 갱신뿐입니다. JSON/Secret 정적 검사, git diff --check와 로컬 입력/artifact git-ignore 확인을 수행합니다. 실행 코드를 바꾸지 않아 CI Run 36688256340의 29개 PASS/20개 unit/14개 Mock Plan 결과를 유지합니다. 실제 AWS/HCP 변경, Secret 등록, MCP 실조회, Module Tag 게시, Apply/Destroy는 수행하지 않았습니다.

## 운영 기본값 위임·State 준비·실제 읽기 전용 Plan — 2026-09-30

사용자는 네트워크, State, Owner/Bucket 이름을 맡겼습니다. 이 선택을 다시 요청하지 않고 승인된 자격증명으로 기존 EC2 네트워크/DNS/NACL/AMI를 조회했습니다. 같은 AZ active NAT를 가진 Private App Subnet을 선택했고 기존 네트워크/TFE를 수정하지 않았습니다. HCP entitlement GET에서 Sentinel/Private Registry/State 저장이 활성, Policy Set 0개로 확인됐습니다. 조직 plan identifier만 보고 기능을 판정하지 않았습니다. 대상 OIDC/Role GET은 NoSuchEntity, 새 State Workspace 이름 GET은 404로 기록했습니다. 생성 직전 충돌을 다시 확인해야 합니다.

변경: scripts/operator_preparation.py, prepare-operator-workspaces.py, tests/unit/test_operator_preparation.py, docs/10-operator-state-and-review.md. Host credit_specification은 T2/T3/T3a에 Standard를 설정하여 surplus credit 과금을 방지하고 다른 클래스에는 해당 설정을 전달하지 않습니다. 기존 Cloud 보고서/lockfile/조회 응답은 보존합니다. 새 생성기는 실제 API/Terraform을 호출하지 않고 검토 Root, 비활성 HCP cloud overlay, Local State 설정 2개, SHA256과 기존 게시물만 생성합니다. Secret/State/임의 파일/symlink/활성 backend를 차단하고 기존 출력은 거부합니다.

검증: Python 24개 PASS, static_checks/preflight(14개 Mock run) PASS, pinned Terraform fmt PASS, 게시 ZIP 3개 검사 PASS. 공식 Terraform 1.13.5 darwin_arm64 SHA256 대조 후 실제 Provider 6.14.1 init/validate/조회 Plan을 격리 Root에서 수행했습니다. 최초 readonly lockfile 시도는 macOS hash 부족으로 validate FAIL; 사본 lockfile만 플랫폼 hash를 추가한 재시도와 Standard 모드 반영 최종 Plan은 PASS입니다. Host 6개/Identity 5개 신규, 수정/삭제 없음. STS 계정 일치 확인 후 Plan했고 HCP State/Token을 Plan에 주입하지 않았습니다. 전체 로그/Plan/실제 ID는 Git 제외 artifact에 둡니다. 검토 Plan은 Apply용이 아닙니다.

비용: AWS 공식 서울 공개 카탈로그를 스트리밍 조회해 t3.small Linux Shared $0.026/h, gp3 $0.0912/GiB-month를 추출했습니다. 선택 SKU/term과 버전을 별도 seoul-host-price-20260930.json으로 보존합니다. 추정 awsstatic feed URL들은 HTTP 오류로 실패해 근거로 쓰지 않았습니다. 첫 생성 범위는 HCP Project 1개/Local State Workspace 2개와 AWS 11개입니다. 실제 생성·배포·Registry 게시·Policy Run·S3 Apply·Token 등록은 전혀 수행하지 않았습니다. 새 실행 코드의 전체 Linux CI는 main 게시 후 확인합니다.

### 운영 준비 main 게시·전체 CI·증거 다운로드

일반 Git push가 PASS로 구현 Commit 2ddc772f034a2a8335aaeaae0fa9885ad010a7b7을 main에 직접 게시했습니다. 자동 Run이 없어 검증 전용 workflow_dispatch를 실행했습니다. Run 36693140577의 completed/success, 정확한 head SHA와 모든 Job/Step 성공을 API와 gh run watch --exit-status로 확인했습니다. Artifact ID 11086677615/22,566 bytes/expired=false를 조회하고 다운로드 종료 코드 0입니다. 전체 29개 PASS, Python 24개, Terraform Mock Plan 14개, Sentinel Mock 12개와 MCP Mock 조회를 대조했으며 다운로드 ZIP 재검사도 PASS입니다. 새 CI 증거는 operator-ci-evidence-20260930에 기존 증거와 별도로 보존합니다. 최종 변경은 보고서와 문서 EOF 정리뿐입니다. 정적 JSON/Secret 검사와 git diff --check 후 게시하며 AWS/HCP 실제 변경은 없습니다.

## AWS 생성 승인 후 실제 배포·검증 — 2026-09-30 KST

사용자 “AWS는 비용 신경쓰지말고 생성해도 돼”를 AWS 기반 인프라 생성 승인으로 적용했습니다. 앞선 네트워크/State/이름 선택 위임을 유지했습니다. HCP 생성 질문은 생성 승인으로 해석하지 않았으며 HCP에는 GET만 수행했습니다.

| 명령·검사 | 결과 | 실제 범위 |
|---|---|---|
| AWS STS 및 예정 HCP Workspace GET 재조회 | PASS | 계정 일치, Workspace 3개 404, HCP 쓰기 없음 |
| S3 backend bootstrap/API 재조회 | PASS | BucketOwnerEnforced, SSE-S3, Versioning, Public Block, non-TLS Deny |
| 배포 사본 terraform init/validate/새 plan | PASS × 2 | backend 연결 후 create-only Host 6/Identity 5; 검토용 이전 Plan 미사용 |
| terraform apply approved.tfplan | PASS × 2 | Terraform 11개 생성; 기존 공유 자원 수정·삭제 없음 |
| EC2/SSM/EBS/SG/IAM 조회와 SSM 호스트 명령 | PASS | running/상태 ok/Online, 실제 AL2023/Docker/Agent, 암호화 EBS·Ingress 0·exact 정책 |
| State head/list versions/잠금·백업 | PASS | 암호화와 Version ID, active lock 없음, 로컬 백업 |
| 실제 호스트 MCP 설치·network=none Mock probe | PASS | 고정 Image initialize/조회 도구 6개/Mock Module tools/call/쓰기 도구 거부 |
| 첫 SSH 공개키 연결 | FAIL → 수정 후 PASS | sshd 사용자에게 Root 0600 파일 읽기 불가; Root 0644로 수정, 파일·디렉터리 사용자 쓰기 없음 |
| SSH over SSM와 Token 부재 런처 | PASS | 인증된 SSM에서 얻은 host key 엄격 확인; 인증 후 Token 부재 거부, stdout 없음 |
| 격리 컨테이너의 실제 TLS/IMDS | PASS | HCP 공개 ping 204, IMDS는 transport에서 차단 |
| post-apply terraform plan -detailed-exitcode | PASS × 2 | S3 State와 실제 계정 대조, exit 0/no changes |
| prepare-demo/verify-prepared-demo | PASS | 파일 준비 6개, ZIP 3개 검사; SSM IAM은 파일 준비만, 정책 연결 없음 |
| Python unittest, bash -n, git diff --check | PASS | 단위 테스트 24개; 공개키 수정의 의미 있는 검증은 실제 SSH 재연결 |
| 실제 HCP Registry/Run/Token/AI Client | 미수행 | 최소 Token/게시·HCP 변경 승인 범위 필요 |

실제 비민감 값·SSM 명령 응답·Plan/Apply/State는 Git 제외 .artifacts/aws-deployment-20260930에 있습니다. Root user_data/State/Git에 AWS/HCP Token이나 Private Key를 넣지 않았습니다. 로컬 전용 Private Key는 외부 호스트에 업로드하지 않았습니다. HCP Workspace 설정 제안에는 실제 Plan/Apply Role output을 채웠으나 적용하지 않았습니다.

변경 파일: 설치 스크립트 공개 authorized_keys 읽기 권한, docs/11-aws-created.md, 최신 안내/입력·승인 상태/비식별 배포 보고서입니다. 기존 Terraform/Module/Policy/CI 및 Cloud 검증 증거는 보존했습니다. 후속 CI 결과는 별도 배포 CI 증거로 기록합니다.
