# 운영 State와 실제 계정 Plan 검토

사용자는 2026-09-30 네트워크, State, Owner/Bucket 이름의 선택을 위임했습니다. 조회한 기존 환경에서 선택한 값은 Git 제외 configs/demo-inputs.local.json에 보관합니다. 같은 선택을 다시 요청하지 않습니다.

| 범위 | 선택 |
|---|---|
| Host | 서울, t3.small, 허용 패턴의 AL2023 x86_64 단일 AMI |
| 네트워크 | 기존 Private App Subnet, 같은 AZ 기존 active NAT, DNS/NACL 조회 확인 |
| 관리 | SSM, Public IP/기본 Inbound 없음, HTTPS egress, IMDSv2, 암호화 gp3 20 GiB |
| CPU credits | T2/T3/T3a Standard; 크레딧 소진 시 성능 제한, surplus credit 추가 과금 방지 |
| Host State | mcp-host-state, HCP Local 실행 |
| Identity State | hcp-aws-identity-state, HCP Local 실행 |
| S3 시연 | aws-ai-demo, 별도 HCP Remote 실행, auto_apply=false |
| OIDC | IAM GET이 NoSuchEntity를 반환해 신규 생성 계획; exact Workspace/한 Bucket 권한 |

HCP Local 실행은 운영자 CLI에서 실행하고 HCP에 State를 보관합니다. Workspace 변수/Variable Set을 평가하지 않으므로 AWS 임시 자격증명은 운영자 프로세스 환경에만 전달합니다. HCP의 잠금/State 버전을 사용하고 전체 State 공유는 비활성화합니다. Sentinel 시연은 Remote Workspace에서 수행합니다.

## 준비와 검토

Python 3.11 이상과 scripts/requirements-validation.txt의 parser를 사용합니다.

```bash
python3 scripts/prepare-operator-workspaces.py --config configs/demo-inputs.local.json --output .artifacts/operator-prepared
python3 scripts/verify-prepared-demo.py --prepared .artifacts/operator-prepared/publication
```

생성기는 외부 API/Terraform을 호출하지 않습니다. 기존 출력 덮어쓰기, symlink/Secret, allowlist 파일 안의 활성 backend/cloud를 거부합니다. State와 임의 파일을 복사하지 않습니다.

| 출력 | 용도 |
|---|---|
| review/{mcp-host,hcp-aws-identity} | backend/cloud 없는 검토 사본과 inputs.tfvars.json |
| state-overlays/*/backend.tf | 승인 후 별도 배포 Root에 복사할 HCP 설정; 자동 활성화하지 않음 |
| hcp-state-settings.json | Local Workspace 2개, auto_apply/global_remote_state=false |
| manifest.json | 원본 사본 SHA256, 외부 변경 없음, 검토 Plan Apply 불허 |
| publication/ | 기존 게시 패키지/입력 |

확인한 계정의 임시 자격증명을 프로세스 환경에 전달한 뒤 검토 Root에서 아래 명령을 수행합니다. 자격증명 값을 파일/명령/로그에 넣지 않습니다.

```bash
terraform init -backend=false -input=false -no-color
terraform validate -no-color
terraform plan -input=false -no-color -var-file=inputs.tfvars.json
```

Terraform 1.13.5/AWS Provider 6.14.1을 유지합니다. init은 공식 체크섬 확인 후 사본 lockfile에 현재 플랫폼 hash를 추가할 수 있습니다. Linux hash만 있는 원본을 macOS에서 -lockfile=readonly로 init한 첫 시도는 이후 validate에서 checksum 불일치로 실패했습니다. 사본에 macOS hash를 추가한 재시도는 PASS이며 원본 lockfile/기존 증거는 보존했습니다.

빈 Local State에서 Host 신규 6개, Identity 신규 5개 Plan이 PASS이고 수정/삭제는 0개입니다. root EBS는 EC2 resource에 포함됩니다. 이 검토는 기존 전체 자원의 부재, 생성 권한/SCP, AMI 부팅/SSM, MCP 연결을 증명하지 않습니다. 검토 Plan은 Apply하지 않습니다. 승인 후 Workspace/State 충돌을 재조회하고 별도 배포 Root에 HCP 설정을 활성화하여 새 Plan을 수행합니다. cloud 설정이 있는 init은 외부 Workspace/State 변경을 일으킬 수 있습니다.

## 첫 생성 범위와 정리

첫 변경 계획은 새 mcp-demo HCP Project와 Local State Workspace 2개, AWS Plan의 11개 자원입니다. Host는 EC2/EBS, SG/HTTPS egress, SSM Role/Profile/정책 연결입니다. Identity는 OIDC Provider, 분리된 Plan/Apply Role 2개와 한 Bucket IAM 정책 2개입니다.

Registry/Policy/Remote Workspace 설정, 다른 Git Repo/Tag, 데모 S3 Apply, MCP Token 주입은 후속 범위입니다. 조직 entitlement GET에서 Sentinel/Private Registry/State 저장 활성과 Policy Set 수용 여유를 확인했지만 실제 정책 Run은 미실행입니다. 실제 대상/전체 Plan/입력/조회 응답은 Git 제외 artifact에, 공개 보고서는 비식별 요약으로 보관합니다.

실패 시 생성 자원과 State를 대조하고, 승인에 포함된 경우 이번에 생성한 자원만 정리합니다. 시연 종료 시 S3 데이터/버전 확인 후 S3 시연 자원 → Identity → Host 순서로 정리합니다. OIDC가 다른 Workspace에서도 사용되면 삭제하지 않습니다. 기존 VPC/Subnet/NAT/TFE는 정리 대상이 아닙니다. HCP State/감사 자료는 보존하며 Workspace/Project 삭제는 별도 범위로 확인합니다.

## 공식 비용 근거

2026-09-30 AWS 공개 서울 가격 카탈로그의 두 SKU/On-Demand term을 직접 추출해 reports/seoul-host-price-20260930.json에 보존했습니다. version=20260925174521, publicationDate=2026-09-25T17:45:21Z입니다.

| 요소 | 단가/기본 예상 |
|---|---|
| t3.small Linux Shared On-Demand | $0.026/시간 |
| gp3 20 GiB, 기본 IOPS/throughput | $0.0912/GiB-month, 월 $1.824 |
| 합계 단순 환산 | 730시간 기준 월 $20.804, 하루 약 $0.684 |
| 별도 사용량 | 기존 NAT 처리 데이터/데이터 전송, 기존 HCP 계약·사용량 요금 |

할인/세금/Free Tier를 적용하지 않은 기본 환산이며 실제 EBS 청구 기간/사용량에 따라 달라집니다. EC2를 Stop해도 EBS 비용은 남습니다. 새 VPC/NAT/ALB/Public IPv4는 계획에 포함되지 않습니다.

공식 근거: [HCP 실행 모드](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/settings), [AWS 서울 가격 카탈로그](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/ap-northeast-2/index.json), [EC2 요금](https://aws.amazon.com/ec2/pricing/on-demand/), [EBS 요금](https://aws.amazon.com/ebs/pricing/).

