# terraform-ai-mcp-demo

AWS AI + Terraform MCP + HCP Private Registry 데모의 코드·검증·운영 준비 저장소입니다. **후속 작업과 결과물은 [이 저장소의 main](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/tree/main)에 둡니다.** Phase 1은 [PR #1](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/pull/1)로 병합됐습니다.

휴대폰에서 시작하려면 [START_HERE.md](START_HERE.md), [현재 완료 상태](reports/cloud-completion.md), [남은 실제 입력](reports/required-inputs.md)을 확인하세요. Cloud에서 가능한 준비는 Phase 2 이후의 게시·연결·시연까지 이어서 작성합니다. **실제 AWS/HCP 리소스 생성과 실제 Private Registry 조회는 아직 수행하지 않았습니다.**

| 경로 | 역할 |
|---|---|
| `infra/mcp-host/` | EC2, 암호화 EBS, IMDSv2, 기본 Inbound 없는 SG, SSM |
| `infra/hcp-aws-identity/` | HCP OIDC exact subject, Plan/Apply Role 분리 |
| `services/terraform-mcp/` | 고정 Image, 조회 allowlist, stdio 런처, metadata 차단 |
| `packages/terraform-aws-s3-standard/` | S3 Module 및 Mock Plan 테스트 |
| `packages/aws-ai-demo/` | Private Registry Root 템플릿, Owner 누락/수정 patch |
| `packages/terraform-demo-policies/` | Sentinel hard-mandatory 및 12개 Mock |
| `configs/demo-inputs.example.json` | 계정별 비민감 입력; 미정값은 null |
| `scripts/prepare-demo.py` | 게시용 ZIP 3개, SHA256, 확인된 입력 파일 생성 |
| `scripts/rehearse-demo.py` | Root만 수정하는 정상/누락/수정 정책 리허설 |
| `scripts/validate-phase1.sh` | 자격증명 없는 전체 검증과 Mock MCP 조회 |
| `docs/`, `reports/` | 한국어 운영 절차, 검증 증거와 실제 연결 제한 |

```bash
bash scripts/install-validation-tools.sh
# 출력된 tool directory를 PATH에 추가한 뒤 실행합니다.
bash scripts/validate-phase1.sh
python3 scripts/prepare-demo.py --config configs/demo-inputs.example.json --output .artifacts/prepared
```

검증은 Terraform fmt/init/validate, network=none Mock Plan 10개, Sentinel Mock 12개, Python 안전 검사, MCP initialize/tools/list/조회 tools/call과 외부 도구 차단을 포함합니다. 시연 리허설은 **정상 정책 통과 → Owner 누락으로 실패 → Root만 수정하여 통과**를 확인합니다. 이 결과는 실제 HCP Run, Private Registry 게시 또는 AWS 배포 증거가 아닙니다.

문서 순서: [사전 준비](docs/00-prerequisites.md) → [코드 검증](docs/01-code-validation.md) → [AWS 준비](docs/02-mobile-aws-setup.md) → [Registry/Workspace](docs/03-registry-and-workspace.md) → [MCP 연결](docs/04-mcp-connection.md) → [시연](docs/05-demo-and-recording.md) → [정리](docs/06-cleanup.md). [Cloud에서 가능한 준비](docs/09-cloud-preparation.md)와 [휴대폰 재개](docs/08-without-pc.md)도 확인하세요.

CI는 자격증명 없는 검증만 실행합니다. 자동 Apply/Destroy, AWS/HCP 관리자 자격증명, 자동 Module Tag 게시는 포함하지 않습니다. 실제 환경의 대상·권한·State·비용과 시연 Client는 별도로 확인해야 합니다.
