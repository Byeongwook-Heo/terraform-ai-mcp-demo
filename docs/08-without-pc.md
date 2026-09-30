# PC 없이 이어서 할 작업

지금은 휴대폰과 Codex Cloud로 결과물 보관, 코드 리뷰, 비민감 입력값 확인, Phase 2 변경안 준비까지 진행할 수 있습니다. 이번 요청은 작업 정리이며 실제 AWS/HCP 배포 승인은 아닙니다.

## 지금 할 수 있는 작업 — 추천 순서

| 순서 | 작업 | 휴대폰에서 사용할 곳 | 완료 기준 |
|---|---|---|---|
| 1 | Phase 1 결과물 검토 | GitHub 작업 Branch·Draft PR, 보고서 | 검증 결과와 실환경 미검증 항목 확인 |
| 2 | Codex Cloud 후속 작업 연결 | Codex Cloud 저장소 선택 화면 | `terraform-ai-mcp-demo`와 작업 Branch 선택 |
| 3 | HCP 사용 조건 확인 | HCP Terraform 웹 또는 Organization 담당자 | Organization 이름, Sentinel 사용 가능 여부, VCS/Registry/Workspace 설정 권한 확인 |
| 4 | AWS 배포 대상 정보 확인 | AWS Console, 기존 환경 담당자 | 데모 Account ID, Region, 기존 VPC/Subnet, AL2023 AMI, egress 경로 확인 |
| 5 | 데모 이름·담당자 결정 | 메모 또는 이 대화 | Project/Workspace, Bucket 이름 후보, Owner Tag 값, PR 리뷰/Apply 담당자 결정 |
| 6 | 코드·문서 보완 요청 | Codex Cloud | 실제 비민감 값으로 example/템플릿을 보완하고 계정 없는 검사 수행 |
| 7 | 시연 흐름 준비 | 시연 문서와 휴대폰 메모 | 조회 → PR → Policy 실패/수정 → 리뷰 → 별도 Run/승인 설명과 녹화 장면 확정 |

준비용 저장소는 **[Byeongwook-Heo/terraform-ai-mcp-demo](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo)**로 확정했고, Phase 1 결과물을 **[Draft PR #1](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/pull/1)**에 게시했습니다. 작업 Branch는 `codex/phase1-terraform-mcp`입니다. 휴대폰에서 PR을 열어 확인하고, 다음 Codex Cloud 작업에서도 같은 저장소와 Branch를 선택하세요. 실제 게시 상태와 후속 요청 예시는 [저장소 안내](../reports/repository.md)에 있습니다. main Push, Merge, Version Tag 게시의 기존 승인 경계는 유지합니다.

AWS/HCP 확인은 운영자가 자신의 휴대폰에서 로그인해 읽는 작업입니다. Codex에 Token이나 AWS Key를 제공할 필요가 없습니다. HCP 메뉴가 보이지 않으면 권한 부족인지 entitlement 미지원인지 확인하고, 확인되지 않은 값은 `미확인`으로 기록합니다.

VPC의 이름만으로는 Subnet의 인터넷 접근을 알 수 없습니다. Route Table과 기존 NAT/승인 proxy 또는 IGW 경로를 확인하세요. SSM endpoint만 있는 Subnet은 Docker Image와 HCP에 접속할 별도 경로가 필요할 수 있습니다. 새 NAT Gateway나 VPC를 기본 준비 작업으로 생성하지 않습니다.

## 휴대폰으로 가능하지만 별도 승인이 필요한 작업

| 작업 | 필요한 조건 | 확인 결과 |
|---|---|---|
| Module 게시와 HCP Registry/Workspace/Policy Set 설정 | 저장소·Tag 게시 및 HCP 외부 설정 변경 승인, Sentinel entitlement | 실제 Source/Version, Policy 적용 대상, Auto-apply 비활성 상태 |
| EC2·EBS·SG·SSM Profile·OIDC/IAM 구성 | 실제 대상, 비용, State 저장/잠금/백업, 변경·정리 범위 승인 | 승인된 리소스와 권한 분리 |
| Docker/MCP 설치·Token 런타임 주입 | 전용 EC2의 브라우저 Session Manager, 최소 조회 Token 발급·회수 절차 승인 | Agent/Container/Guard 상태, 자격증명 비노출 |
| 실제 API 및 MCP Private Module 조회 | 별도 시연 Client, SSH over SSM 권한·key·host key 검증, 실연결 승인 | API 직접 조회와 MCP initialize/tools/list/tools/call 증거를 각각 기록 |

휴대폰 AWS Console과 승인된 CloudShell로 인프라 준비를 수행할 수 있지만, 브라우저 호환성·키보드 입력·CLI 환경은 실제 기기에서 확인해야 합니다. CloudShell은 임시 관리 CLI로 사용하고 중요한 State는 승인된 저장·잠금 경로에 보관합니다. MCP Server는 EC2 Docker에 둡니다.

데모 S3의 Apply는 위 준비 승인과 별개입니다. PR 리뷰/Merge 후 새로운 Standard Run에서 Plan/Policy를 검사하고 담당자가 별도로 승인합니다.

## PC가 없어도 실제 MCP 시연이 가능한 조건

휴대폰의 브라우저 Session Manager는 호스트 관리 경로입니다. 실제 AI 시연에는 Codex CLI/IDE 등 MCP를 호출하는 별도 Client 실행 환경이 필요합니다. 현재 코드 작성용 Codex Cloud에서 그 연결이 자동 제공된다고 가정하지 않습니다.

PC를 사용할 수 없다면 **브라우저로 접속 가능한 별도 원격 개발 환경에서 Codex CLI를 실행하는 방안**을 검토할 수 있습니다. 그 환경에서 Codex 로그인, AWS CLI/Session Manager plugin, SSH stdio, key 보관, Client config, 네트워크 접근을 확인해야 합니다. 실제 제품 지원·비용·접속 방식은 미검증이며 새 환경 생성은 별도 승인 대상입니다. 환경을 확보하기 전에는 시연 대본과 설정 예시 준비까지 진행합니다.

## 다음 작업을 위해 남길 비민감 메모

아는 값만 채우고 모르는 값은 `미정`으로 두세요. Token, Access Key, SSH Private Key, State 원문은 포함하지 않습니다.

```text
기존 준비용 저장소 URL: https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo
AWS 데모 Account ID:
AWS Region: ap-northeast-2 제안
VPC ID / Subnet ID:
AL2023 x86_64 AMI ID:
기존 egress 경로: NAT / proxy / Public Subnet+IGW / 미확인
HCP Organization:
Sentinel 사용 가능 여부: 가능 / 불가 / 미확인
HCP Project / Workspace: mcp-demo / aws-ai-demo 제안
Bucket 이름 후보 / Owner Tag 값:
PR 리뷰 담당자 / AWS 준비 담당자 / Apply 담당자:
시연 Client 환경: PC 추후 사용 / 원격 개발 환경 검토 / 미정
이번 후속 작업 범위: 비민감 값 반영·검토·격리된 검사만
```

저장소를 확정했으므로 다음 순서는 **PR 검토 → HCP Sentinel 확인 → AWS 네트워크·입력값 정리 → Phase 2 변경안 리뷰**입니다. 상세 승인 항목은 [required-inputs.md](../reports/required-inputs.md), AWS 준비 절차는 [02-mobile-aws-setup.md](02-mobile-aws-setup.md), 시연 순서는 [05-demo-and-recording.md](05-demo-and-recording.md)를 확인하세요.
