# Phase 2 실제 입력과 승인

현재 실제 자격증명은 필요하지 않았고 요청하지 않았습니다. Secret 값은 이 문서/채팅/Git에 입력하지 않습니다.

| 구분 | 필요한 비민감 입력/확인 | 상태 |
|---|---|---|
| AWS | Account ID, 승인 Region, 기존 VPC/Subnet, AL2023 x86_64 AMI ID | BLOCKED: 미제공 |
| 네트워크 | Route/DNS/NACL, SSM endpoint, Docker/HCP egress, proxy 여부 | BLOCKED: 미확인 |
| EC2 | t3.small 적합성, 20 GiB EBS/KMS 기준, 비용, 데모 tags | BLOCKED: 미확인 |
| 관리 | 사람 SSO/MFA Role, browser SSM 문서 ARN, session prefix, 접속 감사 | BLOCKED: 미확인 |
| MCP Client | 별도 Client 종류/버전, AWS CLI/plugin, Instance ID, 공개 ed25519 key 및 검증한 host key | BLOCKED: 미제공 |
| SSH | SSM SSH-only IAM Role, sshd 설정, 기본 Inbound 없는 경로 | BLOCKED: 실연결 전 |
| Docker | 172.30.240.0/24 충돌 여부, iptables backend, AL2023 실제 package 버전 | BLOCKED: 실환경 전 |
| HCP | Organization, 정확한 Project/Workspace, Remote run/VCS 연결, Team 접근 | BLOCKED: 미제공 |
| Registry | 실제 namespace/source/version, Module 게시 권한/승인 | BLOCKED: 미게시 |
| Policy | Sentinel entitlement, Policy Set scope, hard-mandatory, Override/Policy 변경 권한 | BLOCKED: 미확인 |
| S3 | 전역 고유 Bucket 이름, 기존 자원/State 존재 여부 | BLOCKED: 미제공 |
| OIDC | 기존 Provider ARN/소유자, audience(client ID), TLS 신뢰, exact subject | BLOCKED: 미확인 |
| 배포 | Plan/Apply Role ARN, SCP/Permission Boundary, 실제 IAM API 허용 여부 | BLOCKED: 실환경 전 |
| Git 준비 저장소 | `Byeongwook-Heo/terraform-ai-mcp-demo`, 작업 Branch `codex/phase1-terraform-mcp` | PASS: 게시·Draft PR #1 생성. 후속 작업도 같은 저장소 사용 |
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
