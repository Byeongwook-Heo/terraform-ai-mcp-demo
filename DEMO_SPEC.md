# AWS 기반 AI + Terraform MCP + Private Registry 데모

## 1. 목적과 상태

세미나 주제는 “딸깍의 진화: AI로 딸깍, 검증은 Terraform으로”이다.
AI가 실제 Private Registry Module을 조회해 변경안을 작성하고, 실제 AWS 변경은 Terraform의 Plan·Policy·담당자 승인 후 수행하는 데모를 만든다.

이 파일은 구현 기준이다. 실행 코드와 격리 검증은 main에 있으며, 최신 완료 상태는 `reports/progress.md`와 `reports/cloud-completion.md`를 확인한다. 실제 AWS/HCP 배포 결과는 아직 없다.
고객의 Azure 환경을 재현하는 작업이 아니다. 테스트 대상은 AWS이며 고객 환경은 변경하지 않는다.
기존 TFE VM은 초기 구성에서 사용하지 않는다. HCP Terraform을 기준으로 작성하되, 실제 사용 가능 Organization과 Sentinel entitlement는 운영자가 확인한다.
HCP Terraform에서 검증한 화면을 TFE 화면 또는 TFE 전체 호환성 검증이라고 소개하지 않는다.

## 2. 기본 구성과 책임 분리

### 코드 제작 경로 — 지금 PC 없이 진행할 부분

휴대폰 → Codex Cloud → 연결한 GitHub 작업 저장소 → 코드·테스트·문서·검토용 변경안

### MCP 정보 조회 경로 — AWS 구성 이후 검증할 부분

시연용 Codex CLI/IDE 등 AI Client → 승인된 원격 연결 → AWS EC2 Docker의 Terraform MCP Server → HCP Terraform Private Registry / Workspace / Run

### 실제 변경 경로

Root Configuration PR → Speculative Plan / Policy → 담당자 리뷰·Merge → 별도의 Standard Run → Plan / Policy → 사람의 승인 → AWS OIDC Role → S3 생성

다음 원칙을 유지한다.
- MCP Server 프로세스와 Docker는 AWS에 둔다.
- Codex Cloud의 임시 작업 컨테이너나 AWS CloudShell을 MCP 상시 서버로 사용하지 않는다.
- 코드 제작용 Codex에 AWS/HCP 배포 관리자 권한이 있다고 가정하지 않는다.
- 사용자 PC의 SSH 설정이나 MCP 설정이 Codex Cloud에 자동으로 전달된다고 가정하지 않는다.
- 고객 환경이나 기존 VM 접근 권한을 요청하지 않는다.

## 3. 작업 저장소와 게시 저장소

처음에는 Codex에 연결할 준비용 저장소 하나에서 산출물을 작성한다.
외부 저장소를 실제로 생성하거나 게시하는 것은 승인 후 별도 작업이다.

권장 준비용 디렉터리:

```text
AGENTS.md
DEMO_SPEC.md
START_HERE.md
infra/mcp-host/                 # EC2·SG·SSM·네트워크 입력
infra/hcp-aws-identity/         # HCP→AWS OIDC trust / IAM
services/terraform-mcp/         # Docker launcher, 보안·설정 예시
packages/terraform-aws-s3-standard/ # 게시할 표준 Module 원본
packages/aws-ai-demo/           # 게시할 Root Configuration 원본
packages/terraform-demo-policies/   # Sentinel와 Mock 테스트
client-configs/                # Codex TOML / 선택적 VS Code JSON 예시
scripts/                       # 승인된 운영자용 설치·검사·정리 스크립트
tests/                         # 네트워크 없는 테스트와 별도 통합 테스트
reports/progress.md
reports/references.md
reports/required-inputs.md
docs/00-prerequisites.md
docs/01-code-validation.md
docs/02-mobile-aws-setup.md
docs/03-registry-and-workspace.md
docs/04-mcp-connection.md
docs/05-demo-and-recording.md
docs/06-cleanup.md
```

후속 게시 대상의 제안 이름:
- terraform-aws-s3-standard
- aws-ai-demo
- terraform-demo-policies

각 게시 저장소에도 필요한 AGENTS.md를 포함하도록 안내한다. 준비용 저장소의 상위 지침이 다른 저장소에 자동 적용된다고 가정하지 않는다.

## 4. 필요한 값과 기본 제안

| 입력 | 처리 |
|---|---|
| AWS account ID | 미정. 실연결 전에 운영자가 확인 |
| AWS Region | ap-northeast-2를 제안값으로 사용 |
| HCP hostname | app.terraform.io |
| HCP Organization | 미정. 임의의 실재 조직을 사용하지 않음 |
| HCP Project | mcp-demo 제안 |
| HCP Workspace | aws-ai-demo 제안 |
| Private Module | s3-standard / aws / 1.0.0 제안 |
| GitHub owner와 저장소 | Byeongwook-Heo/terraform-ai-mcp-demo, 공개 저장소의 main |
| VPC/Subnet | 운영자가 제공. Default VPC 존재를 가정하지 않음 |
| EC2 instance type | 단일 사용자 Lab용 소형 x86_64 인스턴스 제안, 비용 확인 |
| MCP Image | 공식 릴리스·도구 지원을 확인하고 버전 고정 |
| Terraform/Provider | 호환되는 버전을 선택·기록, 임의 latest 사용 금지 |
| S3 Bucket 이름 | 고유 이름을 운영자가 확정 |
| MCP TFE_TOKEN | 운영자가 안전한 런타임 경로로 주입. 문서/Git 금지 |
| HCP 정책 기능 | Sentinel 사용 가능 여부 미확인. 실제 연결 전 확인 |

미정인 Registry Source나 IAM ARN은 템플릿으로 둔다. 존재하지 않는 Module을 실제 Private Registry에서 가져왔다고 기록하지 않는다.
완성되지 않은 템플릿을 활성 Terraform root에 섞어 검증 성공을 왜곡하지 않는다.

## 5. Phase 1 — 지금 허용된 작업: 코드·문서·테스트

### 5.1 EC2 및 원격 관리

Amazon Linux 2023 x86_64 기반을 제안한다. 암호화 EBS, IMDSv2, 리소스 Tag를 포함한다.
기존 승인 VPC/Subnet을 입력받는 구성을 우선하며, NAT Gateway·ALB·새 VPC 등 추가 비용 요소를 임의 생성하지 않는다.
네트워크가 미정이면 필요한 egress와 대안을 문서화하고 실제 Plan/Apply는 하지 않는다.

휴대폰에서 관리하기 위해 Session Manager를 기본 관리 경로로 준비한다.
- SSM Agent의 설치/활성 여부 검증
- Instance Profile의 SSM 관리 권한 또는 기존 관리 구성을 확인
- 접속 사용자 IAM 권한과 EC2→SSM endpoint 연결 요건 문서화
- 기본 Inbound 개방 없음
- 이 관리 Role에 데모 S3 배포 권한을 추가하지 않음
- 외부 Docker Image와 HCP 접근에는 별도의 인터넷/프록시 경로가 필요함을 설명

Session Manager 브라우저 Shell은 호스트 관리 경로이다. 그것만으로 로컬 Codex의 MCP stdio가 연결되는 것은 아니다.
시연 AI 연결은 아래 중 하나를 승인받아 별도로 검증한다.
1. 제한된 SSH+stdio 연결. SSH는 고정된 승인 원본만 허용하고 키/명령 권한 제한.
2. SSH over Session Manager 등 별도 터널. CLI plugin/SSH daemon/권한 요건까지 검증.
3. 인증·TLS를 포함한 Streamable HTTP. 기본 구현에 추가하지 말고 별도 설계안으로 취급.

### 5.2 MCP Server

공식 hashicorp/terraform-mcp-server 이미지를 사용하고 태그 또는 검증한 digest를 고정한다.
선택 버전에서 지원하는 실행 명령, 환경 변수, Tool 이름을 공식 문서와 --help로 확인한다.
초기 조회 allowlist 후보:
- search_private_modules
- get_private_module_details
- list_workspaces
- list_runs
- get_run_details
- get_token_permissions

지원하지 않는 도구는 보고하고 임의 이름으로 대체하지 않는다.
ENABLE_TF_OPERATIONS=false와 Token 최소권한, Tool allowlist를 함께 사용한다.
Secret은 이미지·user_data·Terraform 변수/State에 넣지 않는다.
Root 소유 환경파일 또는 승인된 Secret 주입 방식을 설계하되, 운영자가 주입하기 전에는 연결 테스트를 수행하지 않는다.
MCP가 실행되는 계정, Docker 실행 권한, 호스트 변경 권한을 분리한다.
Token을 제공하는 SSM/Secret 저장소 경로가 있다면 최소 Get 권한과 로그 노출을 검토한다.

stdio는 Client가 세션을 열 때 프로세스가 실행되는 구조이다. systemd 상시 HTTP 서비스로 바꿀 때는 인증·접속 제어를 새로 설계한다.

### 5.3 Codex Client 설정

Codex CLI/IDE의 config.toml 예시를 작성한다. VS Code 내장 AI용 mcp.json을 Codex 설정으로 복사하지 않는다.
실제 hostname, SSH alias, key 경로, Token은 placeholder로 남긴다.
구축용 Codex Cloud의 연결 검증과 시연용 Client의 연결 검증을 구분한다.
현재 Cloud 환경의 Tool·네트워크 지원을 확인하지 않고 SSH/stdin 서버가 그대로 지원된다고 주장하지 않는다.

### 5.4 Private S3 Module

다음 리소스를 생성하는 재사용 Module을 만든다.
- aws_s3_bucket
- aws_s3_bucket_public_access_block
- aws_s3_bucket_versioning

필수 Input: bucket_name
선택 Input: tags, 기본 {}
기본 동작: Public Access Block 적용, Versioning Enabled, ManagedBy=Terraform
Output: bucket_id, bucket_arn
force_destroy=false. 테스트 Bucket에 실제 데이터를 넣지 않음.

Owner는 Module의 필수 Input이나 validation으로 차단하지 않는다.
Owner 누락 시 Terraform Plan이 가능하고 Sentinel이 실패하는 데모가 목적이다.

### 5.5 Root Configuration

Private Registry의 source와 version을 사용하는 Root를 만든다.
Registry 게시 전 단위 테스트용 local module harness와, 실제 Private Registry를 쓰는 최종 root를 분리한다.
최종 시연에서 local source로 실행한 것을 Private Registry 사용 성공이라고 설명하지 않는다.
Source·Version·bucket_name·태그만 명확히 노출한다. AWS Key를 작성하지 않는다.
Root Provider는 Region을 명시한다. Owner를 provider default_tags로 자동 추가하지 않는다.
정상/Owner 누락/수정 후 시나리오를 재현 가능한 patch 또는 명시된 fixture로 제공한다.

### 5.6 AWS 인증

HCP Terraform→AWS OIDC 구성을 작성한다.
신뢰 조건은 Audience, Organization, Project, Workspace, run_phase를 제한한다.
Plan·Apply Role을 분리하거나 단일 Lab Role의 범위를 명확히 설명한다.
MCP EC2의 호스트 관리 Role과 배포 Role은 별개다.
S3 작업의 IAM Action은 선택 Provider에 필요한 조회·변경을 확인해 제한한다.
모든 서비스 관리자 권한이나 무제한 s3:*를 기본값으로 만들지 않는다.
기존 OIDC Provider가 있으면 재사용/import 방안을 안내하고 중복 생성하지 않는다.
실제 OIDC Provider/Role 생성은 Phase 2 승인 이후다.

### 5.7 Policy

Sentinel tfplan/v2 기반으로 관리 대상 aws_s3_bucket에 비어 있지 않은 Owner Tag가 있는지 검사한다.
순수 삭제는 검사에서 제외한다.
정상, Owner 누락, 빈 Owner, 무관한 Resource, 삭제 시나리오의 Mock 테스트를 제공한다.
Hard mandatory를 제안하고, Policy Set의 Override 허용과 사용자 우회 권한을 확인한다.
Sentinel entitlement가 없으면 문법/Mock 테스트까지만 보고한다. OPA로 자동 변경하거나 정책 기능이 있는 척하지 않는다.

### 5.8 검증과 CI

- Terraform fmt / init -backend=false / validate를 실행 가능한 디렉터리별로 수행
- Registry 접근이 필요한 최종 root와 credential-free test root를 분리
- Terraform test는 사전에 검토한 Mock Provider + command=plan 테스트만 실행
- 실제 Provider를 호출하는 apply 기본 테스트는 수행하지 않음
- Sentinel Mock 테스트 수행. CLI가 없거나 설치가 차단되면 이유를 기록
- Shell syntax, TOML/JSON parsing, Secret 포함 여부 점검
- CI는 검증만 수행. AWS/HCP 쓰기 자격증명과 자동 Apply는 추가하지 않음
- 최소한 stdout 오염, 도구 allowlist, 자격증명 비노출을 검사할 수 있는 테스트 설계

Phase 1 완료 조건: 실행 가능한 코드/템플릿과 문서, 실행한 테스트 결과, 미확인 값과 Phase 2 승인 항목이 있다. 실제 배포 완료가 아니다.

## 6. Phase 2 — 운영자 승인 후 원격 환경 준비

Phase 1 변경안을 검토하고 다음을 승인받은 뒤 진행한다.
- 실제 AWS 계정/Region/VPC/Subnet과 HCP Organization
- 예상 생성 리소스와 비용 요소
- State 저장/잠금/백업 경로와 정리 방법
- Repo 게시, Module Tag, HCP Workspace/Policy 연결 권한
- 최소권한 자격증명 주입 방법

권장 순서:
1. Git 게시 저장소와 Module Version 준비
2. HCP Private Registry 게시 및 Source 확인
3. HCP Workspace와 Policy Set, 수동 승인 설정
4. AWS MCP EC2 및 SSM 관리 연결
5. Docker/MCP 설치와 Token 안전 주입
6. HCP→AWS OIDC 및 최소권한 Role 구성
7. API 직접 조회와 MCP 프로토콜 테스트를 따로 실행

CloudShell은 운영자의 임시 CLI로만 사용한다. 검토한 코드를 Git에서 가져오며 중요한 State는 임시 세션에만 남기지 않는다.
직접 API 조회 성공만으로 MCP 구현 완료라고 기록하지 않는다. 통합 검증은 initialize → tools/list → tools/call 결과까지 확인한다.
Phase 2에서는 데모 S3의 최종 Apply를 별도 승인 없이 진행하지 않는다.

## 7. Phase 3 — 시연 Client와 실제 데모 검증

1. 실제 Client에서 AWS MCP 연결
2. 실제 Private Module Source/Version/Input 조회
3. Root Configuration 작성
4. PR의 Speculative Plan 성공
5. Owner 누락 Revision에서 Plan 성공, Policy 실패
6. AI가 Root만 수정하고 Policy는 그대로 유지
7. 사람의 PR 리뷰와 Merge
8. 새로운 Standard Run에서 Plan·Policy 검사
9. Auto-apply 비활성 상태의 승인 대기 확인
10. 담당자 승인 후에만 Apply
11. AWS S3, Public Access Block, Versioning, Tag 확인
12. 정상 재시연과 정리 절차 기록

정책 오류를 사람이 복사해 AI에 전달했다면 자동 수집이라고 설명하지 않는다.
PR Merge와 최종 Apply는 같은 승인이 아니다. Speculative Plan을 Apply하지 않는다.
녹화에는 실제 테스트 플랫폼 HCP Terraform, 데모 환경, 사용 버전을 표시한다.

## 8. 완료 판정과 보고 형식

| 단계 | 완료 증거 |
|---|---|
| 코드 준비 | Commit/변경 파일, formatter/validator 결과 |
| 단위 테스트 | Mock 데이터와 PASS/FAIL 결과 |
| EC2 준비 | Instance/설치 상태, 접근 방식, 실제 버전 |
| HCP API 조회 | 비식별 조회 결과, 호출 경로 |
| MCP 조회 | initialize/tools/list/tools/call의 성공 증거 |
| 실제 시연 | PR, Run ID, Policy fail/pass, 사람 승인, AWS 결과 |

각 결과는 PASS / FAIL / SKIPPED / BLOCKED로 기록한다.
State 원문, Token, SSH Key, 고객 식별자는 보고서에 넣지 않는다.
최종 답변에는 지금 완료한 것, 실제 환경에서 미검증인 것, 다음 승인/입력값을 구분한다.

## 9. 공식 참고자료

아래는 설계 시 확인할 공식 시작점이다. 실행 전 선택 버전의 문서와 릴리스도 다시 확인한다.

- Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md/
- Codex Cloud: https://developers.openai.com/codex/cloud/
- Codex Cloud environments: https://developers.openai.com/codex/cloud/environments/
- Codex MCP: https://developers.openai.com/codex/mcp/
- 현재 연결되는 공식 AGENTS.md 문서: https://learn.chatgpt.com/docs/agent-configuration/agents-md
- 현재 연결되는 공식 Cloud 문서: https://learn.chatgpt.com/docs/environments/cloud-environments
- 현재 연결되는 공식 MCP 문서: https://learn.chatgpt.com/docs/extend/mcp
- Terraform MCP 공식 저장소: https://github.com/hashicorp/terraform-mcp-server
- Terraform MCP Reference: https://developer.hashicorp.com/terraform/mcp-server/reference
- Private Module 게시: https://developer.hashicorp.com/terraform/cloud-docs/registry/publish-modules
- AWS OIDC: https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials/aws-configuration
- Sentinel tfplan/v2: https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement/import-reference/tfplan-v2
- Policy Set: https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement/manage-policy-sets
- Run modes: https://developer.hashicorp.com/terraform/cloud-docs/workspaces/run/modes-and-options
- AWS Session Manager: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html
- SSM prerequisites: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html
- SSM instance permissions: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-instance-profile.html
- AWS CloudShell: https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html
- CloudShell restrictions: https://docs.aws.amazon.com/cloudshell/latest/userguide/limits.html

## 10. 사용자 환경 보완 — 2026-09-30

EC2 AMI 이름은 `hc-base-*`와 `hc-security-base-*`만 허용한다. 선택 ID의 실제 metadata로 확인하고 임의 latest 또는 Amazon 기본 AMI로 대체하지 않는다. 현재 bootstrap은 AL2023 x86_64를 전제로 하므로 실제 허용 AMI의 OS·SSM 호환성은 미확인이다. OS가 다르면 먼저 구현·검증을 변경하며 이름만 보고 배포하지 않는다.
