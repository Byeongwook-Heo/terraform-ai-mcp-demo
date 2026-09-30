# 실제 연결·시연에 필요한 입력과 승인

Cloud 준비에는 실제 자격증명이 필요하지 않습니다. 준비 코드는 main에 두고 실제 환경에 필요한 입력은 아래에 기록합니다. Secret 값은 이 문서/채팅/Git에 입력하지 않습니다.

| 구분 | 필요한 비민감 입력/확인 | 상태 |
|---|---|---|
| AWS | Account ID, 승인 Region, 기존 VPC/Subnet, 허용 이름 패턴의 x86_64 AMI ID/Name/Owner 및 OS·SSM 호환성 | PARTIAL: 계정/서울 리전/AMI 후보 실조회 PASS; VPC/Subnet·배포 대상·부팅/SSM 미확인 |
| 네트워크 | Route/DNS/NACL, SSM endpoint, Docker/HCP egress, proxy 여부 | BLOCKED: 미확인 |
| EC2 | t3.small 적합성, 20 GiB EBS/KMS 기준, 비용, 데모 tags | BLOCKED: 미확인 |
| 관리 | 사람 SSO/MFA Role, browser SSM 문서 ARN, session prefix, 접속 감사 | BLOCKED: 미확인 |
| MCP Client | 별도 Client 종류/버전, AWS CLI/plugin, Instance ID, 공개 ed25519 key 및 검증한 host key | BLOCKED: 미제공 |
| SSH | SSM SSH-only IAM Role, sshd 설정, 기본 Inbound 없는 경로 | BLOCKED: 실연결 전 |
| Docker | 172.30.240.0/24 충돌 여부, iptables backend, AL2023 실제 package 버전 | BLOCKED: 실환경 전 |
| HCP | Organization, 정확한 Project/Workspace, Remote run/VCS 연결, Team 접근 | PARTIAL: 단일 조직 GET/재대조 PASS; 나머지는 미확인 |
| Registry | 실제 namespace/source/version, Module 게시 권한/승인 | BLOCKED: 미게시 |
| Policy | Sentinel entitlement, Policy Set scope, hard-mandatory, Override/Policy 변경 권한 | BLOCKED: 미확인 |
| S3 | 전역 고유 Bucket 이름, 기존 자원/State 존재 여부 | BLOCKED: 미제공 |
| OIDC | 기존 Provider ARN/소유자, audience(client ID), TLS 신뢰, exact subject | BLOCKED: 미확인 |
| 배포 | Plan/Apply Role ARN, SCP/Permission Boundary, 실제 IAM API 허용 여부 | BLOCKED: 실환경 전 |
| Git 준비 저장소 | `Byeongwook-Heo/terraform-ai-mcp-demo`, `main` | PASS: Public, Phase 1 PR #1 병합. 사용자 요청으로 main에서 후속 작업 |
| Git 후속 게시 | Module/Root/Policy 게시 저장소, HCP VCS 권한, branch protection/reviewer | BLOCKED: 준비 저장소 게시와 별개로 확정·승인 필요 |
| State | 호스트/Identity Root의 암호화 저장·잠금·백업, 소유권/정리 절차 | BLOCKED: 미승인 |
| Secret 절차 | 짧은 조회 Token 발급자·Team 권한·런타임 주입·회수, Client Private Key 보관 | BLOCKED: 절차 확정 필요 |

승인은 별도로 다음 범위를 명시해야 합니다.

1. 실제 계정/Region/VPC/Subnet에서 EC2/EBS/SG/SSM Profile/필요 IAM/OIDC 생성·변경, 예상 비용과 대상 State.
2. 승인된 기존 Git 게시 저장소 또는 새 게시 저장소 생성, Module Version Tag 게시, HCP Registry/Workspace/Policy Set 등록·설정.
3. 최소권한 Token 주입 및 실제 API 직접 조회와 MCP initialize/tools/list/tools/call 검증. Codex Cloud에 관리자 Key를 주입하지 않습니다.
4. 실제 시연 PR 리뷰·Merge와 **그 이후 별도 Standard Run의 Apply 승인**. Phase 2 준비 승인만으로 데모 S3 Apply를 수행하지 않습니다.
5. 비용 종료/리소스 정리, 데이터·State·감사 자료 보존 범위. 기존 OIDC Provider/고객 자원은 정리 대상이 아닙니다.

NAT/ALB/VPC endpoint 등 추가 비용 구성, 직접 SSH Inbound /32, 인증된 HTTP MCP는 필요해지면 대상과 영향·정리 계획을 따로 검토합니다. 현재 코드의 기본값에 추가하지 않았습니다.

## 로컬 자격증명 파일 확인 — 2026-09-30

사용자가 지정한 다운로드 폴더의 AWS credentials RTF와 HCP Terraform token TXT의 존재·형식을 확인했습니다. AWS access key/session token의 값이나 HCP token은 출력·저장하지 않았습니다. AWS/HCP 읽기 전용 외부 인증 조회는 자동 승인 검토에서 자격증명 전송 승인이 불명확하다는 이유로 차단됐으므로 계정/Organization/API 권한 확인은 여전히 BLOCKED입니다. 실제 변경 승인은 아직 없습니다.

추가 첨부 `terraform-mcp-codex-handoff.zip`은 다운로드 도구가 파일 ID를 확인하지 못해 내부 문서 대조가 BLOCKED입니다. 이 파일 내용을 기존 저장소 지침으로 간주하거나 추측해 반영하지 않았습니다.

## 읽기 전용 조회 승인 및 완료 — 2026-09-30

사용자가 17:20 KST에 STS/EC2 계정·AMI 및 app.terraform.io 조직 GET의 자격증명 사용을 명시 승인했습니다. 실제 인증·조회와 두 번째 대조는 PASS입니다. 재첨부 ZIP의 3개 지침 읽기도 PASS이며 ZIP에 없는 2개 보고서는 main에서 읽었습니다. 위 최초 BLOCKED 기록은 이력으로 보존합니다. 계정/조직 실값과 AMI 후보는 공개 Git에서 제외한 local 입력과 artifact에만 두었습니다.

여전히 필요한 항목: 기존 VPC/Subnet·egress, 명시적인 후보 AMI 선택 승인·부팅/SSM 확인, State 저장/잠금/백업, Owner/Bucket 이름, HCP Project/Workspace/Registry/Policy 범위와 Sentinel entitlement, MCP용 최소 조회 Token. 이번 승인은 리소스/설정 생성·수정·삭제나 Token 등록/배포 승인이 아닙니다.
