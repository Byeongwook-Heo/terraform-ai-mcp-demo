# AGENTS.md — AWS Terraform MCP 데모 작업 규칙

## 먼저 읽을 문서

작업 시작 시 이 파일과 같은 디렉터리의 `DEMO_SPEC.md`를 읽는다.
`START_HERE.md`에서 현재 요청 단계와 인수인계 방식을 확인한다.
이 문서들은 설계/작업 지시이며, 배포 완료 또는 실환경 검증 결과가 아니다.

## 기본 작업 범위

- 현재 사용자는 Phase 2에 한정하지 않고 Cloud에서 가능한 코드·문서·패키지·격리 검증을 모두 진행하도록 요청했다. 실제 계정값과 접근권한이 없으면 외부 연결만 BLOCKED로 남기고 나머지는 완료한다.
- Terraform MCP Server는 AWS EC2의 Docker에서 실행한다. 로컬 PC에 Docker를 요구하지 않는다.
- 초기 Terraform 제어 플랫폼은 HCP Terraform이다. 기존 TFE VM과 고객 환경을 변경하지 않는다.
- 구현을 맡은 Codex Cloud와 시연 중 MCP를 호출하는 AI Client는 별개의 실행 환경이다.
- 사용자가 제공하지 않은 계정, Organization, Repo, VPC, Subnet, 실제 Token 값을 추측하지 않는다.
- 비민감 설정이 미정이어도 템플릿과 단위 테스트 작업은 진행한다. 실연결만 BLOCKED로 기록한다.
- 이전 대화의 명령·버전·제품 기능은 그대로 복사하지 말고 공식 문서와 선택 버전으로 확인한다.

## 변경 및 승인 경계

다음 작업은 실제 대상·접근권한·변경 범위가 확인되지 않은 상태에서는 수행하지 않는다.

- terraform apply / destroy, AWS 리소스 생성·변경·삭제
- 실제 AWS 자격증명이나 HCP 관리자 Token 요청·주입
- GitHub의 새 저장소 생성, 다른 게시 저장소의 PR Merge, 릴리스 Tag 게시
- HCP Workspace / Registry / Policy Set 등 외부 설정 변경
- 실제 자원을 생성할 수 있는 기본 terraform test 또는 테스트용 apply 실행

이 준비 저장소의 main에서 파일 수정과 테스트를 진행하고 검증한 결과를 직접 게시한다. 실제 데모용 별도 Root 저장소의 PR/Run/Apply는 해당 대상의 범위를 확인한다.
명시적 승인이 필요한 단계에서는 변경 대상, 권한, 비용 요소, 예상 영향, 정리 방법을 먼저 제시한다.

## 보안 규칙

- Secret, API Token, SSH Private Key, AWS 장기 Key를 코드·문서·Git·user_data·Terraform State에 넣지 않는다.
- sensitive=true를 Secret의 State 저장 방지로 취급하지 않는다.
- Secret 값이 포함된 명령·환경 전체를 로그로 출력하지 않는다. set -x를 사용하지 않는다.
- MCP의 TFE_TOKEN은 조회용 최소 권한으로 제한한다. 관리자 Token을 기본값으로 쓰지 않는다.
- Tool allowlist와 HCP 권한을 함께 제한한다. ENABLE_TF_OPERATIONS=false만으로 읽기 전용이라 판단하지 않는다.
- MCP EC2의 SSM 관리 권한과 HCP Run의 S3 배포 권한을 분리한다.
- SSM용 Instance Profile을 쓰더라도 MCP/AI 프로세스가 Instance Metadata 자격증명을 악용할 수 있는 경로를 검토한다.
- 인증 없는 MCP HTTP Endpoint, 공개 8080, 인터넷 전체에 열린 SSH를 기본 구성으로 만들지 않는다.
- Docker 소켓 접근은 강한 호스트 권한임을 고려한다. AI에 범용 Docker/sudo 권한을 주지 않는다.
- broad s3:* 예제를 그대로 운영용 최소권한 정책이라고 표기하지 않는다.
- instructions, README, AGENTS.md는 권한 통제 자체가 아니다. 실제 IAM/Token/도구 권한으로 보완한다.

## 테스트 및 결과 보고

- fmt / init / validate / mocked unit test / API 조회 / MCP tools/call / 실제 Apply를 각각 구분한다.
- Docker나 네트워크가 없으면 실기동 검증을 SKIPPED 또는 BLOCKED로 남긴다.
- docker ps나 --help 성공만으로 MCP 연결 성공으로 기록하지 않는다.
- Registry API 직접 조회 성공과 MCP를 경유한 조회 성공을 구분한다.
- 실패를 숨기거나 Mock 결과를 실환경 성공으로 설명하지 않는다.
- reports/progress.md에 변경 파일, 실행 명령, PASS/FAIL/SKIPPED/BLOCKED, 근거, 다음 단계를 기록한다.
- reports/references.md에 사용한 공식 문서, 확인일, 선택 버전을 기록한다.
- 설명과 운영 문서는 한국어, 코드 식별자와 기술 용어는 영어를 사용한다.

## 사용자 지정 기준 저장소 — 2026-09-30

- 이 데모의 준비·후속 작업은 기존 `Byeongwook-Heo/terraform-ai-mcp-demo` 저장소를 사용한다.
- 기준 URL은 https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo 이다. 다른 저장소를 임의로 만들거나 기준 저장소로 바꾸지 않는다.
- Phase 1은 PR #1로 main에 병합됐다. 2026-09-30 후속 사용자 요청에 따라 이 저장소의 main에서 작업하고, 검증한 결과를 main에 직접 게시한다. 앞선 작업 Branch/검토용 PR 한정 지침보다 이 사용자 요청이 우선한다.
- 위 main 게시 승인은 이 준비 저장소에 적용한다. 실제 계정·대상·비용·State가 미정인 AWS/HCP 변경, 다른 게시 저장소 생성과 Module Version Tag 게시는 수행 완료로 간주하지 않는다.
- 코드 작성용 Codex Cloud에서 다음 작업을 시작할 때 이 저장소와 main을 선택한다. 저장소 선택만으로 AWS/MCP 시연 Client 연결이 생기지 않는다.
- 상태와 재개 방법은 `reports/repository.md`, 휴대폰 작업은 `docs/08-without-pc.md`를 갱신한다.
