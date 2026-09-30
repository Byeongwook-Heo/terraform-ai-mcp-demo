# AWS 생성 결과와 이어서 작업하기

2026-09-30 KST 사용자가 AWS 생성과 비용을 승인했습니다. 앞서 위임한 네트워크·State·이름 선택을 적용해 AWS 기반 인프라를 생성했습니다. HCP에는 GET만 수행했으며 Project/Workspace를 생성하거나 설정하지 않았습니다. 이전 HCP Local State 제안은 [검토 기록](10-operator-state-and-review.md)에 보존합니다.

## 실제 생성한 범위

| 범위 | 생성·검증 결과 |
|---|---|
| Host Terraform | 신규 6개: EC2, SG, HTTPS egress, SSM Role, 관리 정책 연결, Instance Profile |
| EC2에 포함된 EBS | 암호화 gp3 20 GiB, 종료 시 삭제; 별도 Terraform resource 수에 포함하지 않음 |
| Identity Terraform | 신규 5개: app.terraform.io OIDC Provider, Plan/Apply Role 2개, Bucket 범위 정책 2개 |
| State bootstrap | 전용 S3 Bucket 1개와 소유권·암호화·버전 관리·Public Block·TLS 정책 |
| 기존 환경 | 기존 Private Subnet과 같은 AZ의 NAT 사용; 기존 VPC/Subnet/NAT/TFE 수정 없음 |

허용 패턴 `hc-base-*`의 AL2023 x86_64 AMI로 부팅했습니다. t3.small Standard, Public IP 없음, SG Ingress 없음, HTTPS 443 egress, IMDSv2 hop limit 1을 확인했습니다. EC2 running, 인스턴스/시스템 상태 ok, SSM Online을 독립 조회로 다시 확인했습니다. 실제 Host는 Amazon Linux 2023.12.20260918, Docker 25.0.16, SSM Agent 3.3.4624.0입니다.

Plan/Apply Role의 trust는 정확한 Organization/Project/Workspace와 run_phase를 제한합니다. 정책 Resource는 예정된 데모 Bucket 하나이며 EC2의 SSM Role과 분리했습니다. OIDC가 생성됐다는 사실은 HCP Run에서 실제 AssumeRole이 성공했다는 증거가 아닙니다.

## 현재 State와 복구

HCP 변경 승인은 없으므로 Host/Identity는 전용 **S3 backend**로 배포했습니다. CLI로 미리 만든 Bucket은 두 Terraform Root 밖에서 관리합니다. BucketOwnerEnforced, SSE-S3 AES256, Versioning Enabled, 전체 Public Access Block, 비 TLS 접근 Deny를 적용·조회했습니다. backend는 `encrypt=true`, `use_lockfile=true`, `allowed_account_ids`를 사용합니다. 별도 DynamoDB는 없습니다.

State key는 `mcp-host/terraform.tfstate`, `hcp-aws-identity/terraform.tfstate`입니다. 저장된 State의 암호화/Version ID, Apply 후 잠금 해제와 별도 로컬 백업을 확인했습니다. S3 연결 후 **새 Plan**을 저장·검토하고 Apply했으며 이전 빈 State 검토 Plan은 사용하지 않았습니다. 배포 후 두 Root의 실제 Plan은 `-detailed-exitcode` 0, 변경 없음입니다.

| 로컬 경로 — 모두 Git 제외 | 용도 |
|---|---|
| configs/demo-inputs.local.json | 실제 비민감 입력, Instance ID와 확인한 SSM session prefix |
| .artifacts/aws-deployment-20260930/deployment-status.md | 실제 계정·자원·Bucket·State 위치와 운영 안내 |
| .artifacts/aws-deployment-20260930/{mcp-host,hcp-aws-identity}/ | 실제 backend/lockfile/입력/Plan/Apply 로그와 State 백업 |
| .artifacts/mcp-client-20260930/ | 전용 키, 검증한 known_hosts, SSH over SSM 설정 |
| .artifacts/aws-deployed-preparation-20260930/ | 입력 준비 6개 PASS, 게시 ZIP, SSM IAM 템플릿, HCP Workspace 설정 제안 |

다음 실제 Plan은 위 **배포 Root와 같은 S3 backend**에서 수행합니다. 원본 infra 또는 review 사본을 빈 State로 Apply하지 않습니다. 로컬 사본을 잃었다면 실제 Bucket/key를 확인해 backend를 재연결하고 State부터 대조합니다. `create_oidc_provider=true`는 이번 State가 신규 Provider를 소유한다는 뜻이며, 생성됐다는 이유만으로 false로 바꾸면 삭제 Plan이 생길 수 있습니다.

정리는 별도 승인 후 State와 자원을 대조해 수행합니다. State Bucket은 Host/Identity destroy에 포함되지 않습니다. State의 버전·감사 자료와 복구 필요성을 확인하기 전까지 보존합니다. 기존 네트워크와 다른 워크스페이스가 쓰는 OIDC는 정리 대상에 넣지 않습니다.

## MCP 설치와 검증 범위

고정 Terraform MCP 1.3.0 Image/digest, 제한된 `mcp-client`, forced command, 고정 sudo 런처, metadata/호스트 접근 차단을 실제 EC2에 설치했습니다. Docker 그룹과 범용 sudo는 부여하지 않았습니다. 인증된 SSM 경로에서 얻은 host key를 검증한 뒤 SSH over SSM의 공개키 인증에 성공했습니다.

첫 SSH 연결은 Root 0600의 공개 authorized_keys를 sshd의 사용자 권한으로 읽지 못해 실패했습니다. 호스트 로그와 사용자 읽기 검사로 원인을 확인했습니다. **Root 소유 0644**로 바꾸고 사용자에게 파일·디렉터리 쓰기가 없음을 검사했으며 설치 스크립트도 수정했습니다. Token과 SSH Private Key의 0600은 유지합니다.

| 검증 | 결과·한계 |
|---|---|
| 실제 EC2의 고정 Image + network=none Mock API | initialize, 정확한 도구 6개, Mock Module 검색·상세, create_workspace 차단 PASS |
| 실제 SSH over SSM | 공개키 인증·엄격한 host key 확인 PASS; Token 부재 시 고정 런처 거부, stdout 없음 |
| mcp-isolated 컨테이너 | 실제 HCP 공개 ping TLS 응답 204, IMDS transport 차단 PASS |
| 실제 HCP Private Registry tools/call | 미수행: 최소 조회 Token 미주입, Module 미게시 |
| 실제 AI Client 설정·최소권한 IAM 연결 | 미수행: 로컬 SSH 설정과 IAM 파일 준비만 완료 |

`/run/terraform-mcp/token`은 비어 있습니다. 관리자 성격의 제공 Token을 MCP에 주입하지 않았습니다. Mock 프로토콜 성공과 HCP 공개 ping을 실제 Private Registry 조회 성공으로 설명하지 않습니다.

## HCP에 남은 작업

예정한 `mcp-host-state`, `hcp-aws-identity-state`, `aws-ai-demo` GET은 404를 반환했습니다. 이번 작업에서 HCP POST/PATCH/DELETE는 0회입니다. 실제 운영 State는 S3에 있으므로 HCP Local State Workspace 두 개를 만들 필요는 없습니다.

다음 승인 대상은 Project `mcp-demo`와 Remote Workspace `aws-ai-demo`입니다. 제안 설정은 Terraform 1.13.5, `auto_apply=false`, AWS dynamic credentials, 생성된 Plan/Apply Role ARN입니다. 실제 값이 채워진 설정 파일은 로컬 준비 폴더에 있으며 아직 HCP에 적용하지 않았습니다.

후속 게시 저장소/Module Version Tag, Private Registry, Workspace VCS, Sentinel Policy Set/Override, 최소 조회 Token과 실제 MCP 조회, 시연 Standard Run/S3 Apply는 각각 대상과 승인 범위를 확인해 진행합니다. 데모 S3 Bucket은 아직 생성하지 않았습니다.

공개 증거는 [aws-deployment-20260930.json](../reports/aws-deployment-20260930.json), 상세 기록은 [progress.md](../reports/progress.md)에 있습니다. 실제 계정·ARN·State·Private Key·Token은 공개 Git에 넣지 않습니다.

공식 근거: [Terraform S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3), [OpenSSH authorized_keys](https://man.openbsd.org/sshd#AUTHORIZED_KEYS_FILE_FORMAT), [HCP 실행 모드](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings). 확인일 2026-09-30.
