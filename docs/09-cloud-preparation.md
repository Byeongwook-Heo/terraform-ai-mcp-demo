# Cloud에서 끝내는 게시·연결·시연 준비

현재 요청은 main에 결과를 두고 Cloud에서 가능한 준비를 모두 완료하는 것입니다. 실제 AWS/HCP 접속에 필요한 계정값과 자격증명은 아직 없습니다. 준비물 생성은 계정이 없어도 진행하며, 실제 외부 검증은 BLOCKED로 기록합니다.

## 전체 격리 검증

Linux x86_64와 Python 3.11 이상을 사용합니다. Docker daemon과 ShellCheck가 필요합니다. `scripts/install-validation-tools.sh`는 Terraform 1.13.5, Sentinel 0.40.0과 Python parser를 고정 설치하고 HashiCorp SHA256을 확인합니다. GitHub runner에서는 PATH에 자동 등록하며 일반 Cloud shell에서는 출력된 도구 디렉터리를 PATH에 추가합니다.

```bash
bash scripts/install-validation-tools.sh
bash scripts/validate-phase1.sh
```

검증 스크립트는 AWS/HCP 자격증명과 Terraform 사용자 설정을 제거한 별도 환경을 사용합니다. 필요한 공개 HTTPS proxy와 CA trust는 유지합니다. Terraform 테스트는 사전 검사한 `mock_provider aws`와 `command=plan`만 사용하고 Docker `network=none`에서 실행합니다. 외부 Registry Root는 init하지 않습니다.

MCP 검증은 실제 고정 서버 Image를 사용합니다. HCP 대신 같은 network=none namespace의 loopback Mock API로 검색과 상세 `tools/call`을 수행합니다. Module ID, version, bucket_name/tags inputs, outputs를 확인하며 allowlist 밖의 쓰기 도구는 거부돼야 합니다. **실제 Private Registry 조회는 아닙니다.**

Sentinel 리허설은 렌더링한 Registry Root의 태그를 Mock plan 데이터에 옮겨 실제 CLI로 평가합니다. Terraform Mock Plan은 별도의 검증 결과이며 실제 tfplan JSON을 export했다고 설명하지 않습니다. 정상/누락/수정 결과, 정책 SHA256, Root 복원 여부는 `reports/rehearsal.json`에 기록합니다.

## 게시용 패키지와 입력 생성

```bash
python3 scripts/prepare-demo.py --config configs/demo-inputs.example.json --output .artifacts/prepared
python3 scripts/verify-prepared-demo.py --prepared .artifacts/prepared
```

결과는 Module/Root/Policy ZIP 3개, 게시 디렉터리, `checksums.json`, `readiness.json`입니다. 실제 GitHub 저장소 생성, Tag, HCP 등록이나 Terraform 명령을 호출하지 않습니다. 출력 디렉터리가 이미 있으면 덮어쓰지 않습니다.

패키지는 검토한 파일 allowlist로 생성합니다. State, `.env`, 실행 결과, Key와 임의의 Terraform 파일을 포함하지 않으며 symlink와 Secret 패턴을 거부합니다. 각 게시 디렉터리에 독립적인 AGENTS.md를 포함합니다. ZIP의 시간·순서를 고정해 같은 입력이면 SHA256도 같습니다. 압축 파일의 SHA256은 무결성 확인용이며 서명·배포 승인 증거가 아닙니다.

검증기는 ZIP 3개, `checksums.json`, `readiness.json`을 읽으며 압축 해제·외부 호출·Terraform 실행을 하지 않습니다. ZIP 누락과 SHA256 불일치, 필수 파일 누락, 중복 이름, 경로 탈출, State/임의 파일, symlink/암호화 항목, 과도한 크기와 Secret 패턴을 거부합니다. 같은 ZIP byte로 hash와 내용을 검사합니다. 성공 종료 코드는 0, 실패는 1이며 실패 시 입력·파일 원문을 출력하지 않습니다. `pending_input_checks`는 실제 입력을 기다리는 항목 수이고 ZIP 검사 성공과 구분합니다.

GitHub Actions artifact를 받은 뒤에도 이 명령을 사용할 수 있습니다. ZIP과 함께 받은 checksum은 손상·일관성 검사 기준입니다. 신뢰할 수 있는 CI Run/Commit에서 받은 checksum과 대조해야 출처를 확인할 수 있습니다. ZIP과 checksum을 함께 바꾼 변경 전체를 이 도구가 검증된 Commit으로 인증하지 않으며, IAM·Terraform 의미 검증이나 사람의 게시 리뷰를 대체하지 않습니다. `inputs/`의 계정별 설정은 별도 리뷰 대상입니다.

미정값을 채우려면 example을 `configs/demo-inputs.local.json`으로 복사합니다. 이 파일과 `.artifacts/`는 Git에서 제외합니다. **Secret을 적는 파일이 아닙니다.** 허용 필드 외 입력, 잘못된 AWS ID, OIDC 계정 불일치, subject wildcard, S3 예약 이름과 placeholder는 거부합니다. 모르는 값은 null을 유지합니다. 현재 ARN 템플릿은 AWS 상용 partition을 기준으로 하며 China/GovCloud Region은 받지 않습니다.

| 입력이 준비된 범위 | 생성 파일 |
|---|---|
| HCP Organization | 실제 source 문자열이 들어간 Root `.tf`와 Owner patch |
| VPC/Subnet/AMI/Owner | `inputs/mcp-host.tfvars.json`, 기본 SSH Inbound 없음 |
| AWS account/HCP/Bucket/OIDC 선택 | `inputs/hcp-aws-identity.tfvars.json` |
| HCP/Bucket | `inputs/workspace-settings.json`, auto_apply=false |
| AWS account/Instance/session prefix | 전용 Client/관리자 SSM IAM 예시 |

PASS는 위 파일의 생성 성공입니다. 실제 ID의 존재, Region 일치, Bucket 전역 고유성, IAM 허용, HCP entitlement나 배포 성공은 검증하지 않습니다. `create_oidc_provider=true`는 기존 Provider가 없음을 확인하고 승인한 경우에만 입력합니다. 파일 생성 자체는 OIDC를 생성하지 않습니다. Workspace Role ARN은 Identity 배포의 실제 output으로 채우며 추측하지 않습니다.

생성된 IAM 문서는 실제 session prefix, AWS policy evaluation과 SSM 연결을 운영자가 확인한 뒤 사용합니다. Root ZIP의 README와 templates/fixtures는 게시 검토 자료입니다. 실제 HCP Workspace에는 렌더링한 Root `.tf`를 연결하고 local module harness를 사용하지 않습니다.

## 실제 환경에서 이어갈 순서

1. 게시 저장소·Module version과 HCP Registry/Workspace/Policy 범위를 확인합니다.
2. AWS account/Region/VPC/Subnet/AMI/egress 및 State 저장·잠금·복구 방법을 확인합니다.
3. 승인된 환경에서 MCP Host와 HCP OIDC Identity를 각각 준비합니다. 실제 Plan/비용을 검토합니다.
4. HCP에 실제 Plan/Apply Role ARN을 등록하고 auto-apply=false, Policy Set scope와 hard-mandatory를 확인합니다.
5. 전용 EC2에 Docker/guard/stdio launcher를 설치하고 최소 조회 Token을 런타임에 주입합니다.
6. 별도 시연 Client에서 실제 initialize/tools/list/Private Module tools/call을 기록합니다.
7. [시연 절차](05-demo-and-recording.md)대로 PR의 Policy 실패/수정과 별도 Standard Run의 수동 승인 대기를 검증합니다.
8. 실제 S3 Apply/정리는 해당 Run과 자원 범위를 확인한 뒤 수행합니다.

현재 Cloud에서는 위 절차의 코드·패키지·리허설 준비까지 완료합니다. 실제 연결 증거와 비용이 생기는 변경은 입력/접근 환경 없이 완료했다고 표시하지 않습니다.
