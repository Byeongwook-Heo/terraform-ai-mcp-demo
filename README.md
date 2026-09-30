# terraform-ai-mcp-demo

AWS AI + Terraform MCP + Private Registry 데모의 Phase 1 준비 저장소입니다.

**앞으로 이 작업은 [Byeongwook-Heo/terraform-ai-mcp-demo](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo)에서 이어갑니다.** 작업 Branch는 `codex/phase1-terraform-mcp`입니다. 기존 `main`의 README 제목과 이력을 보존하고 검토용 변경안을 추가했습니다.

**AWS/HCP 리소스 배포 및 실제 Private Registry 조회는 수행하지 않았습니다.** 첨부 지침의 기존 내용을 보존했습니다. `AGENTS.md` 끝에 사용자가 지정한 기준 저장소와 후속 작업 규칙만 추가했습니다.

휴대폰에서는 **[Draft PR #1](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/pull/1)**을 열고 [검증·진행 보고서](reports/progress.md), [필요 입력·승인](reports/required-inputs.md), [시연 순서](docs/05-demo-and-recording.md)를 확인하세요. PR을 Merge하기 전에는 `main`에 Phase 1 파일이 없습니다. 저장소 선택·후속 작업 방식은 [저장소 안내](reports/repository.md)에 있습니다.

PC 없이 이어서 할 작업과 추천 순서는 [휴대폰 후속 체크리스트](docs/08-without-pc.md)에 정리했습니다.

| 경로 | 역할 |
|---|---|
| `infra/mcp-host/` | 기존 VPC/Subnet에 EC2, 암호화 EBS, IMDSv2, 기본 Inbound 없는 SG, SSM Profile |
| `infra/hcp-aws-identity/` | HCP OIDC exact subject, Plan 조회 Role / Apply S3 Role |
| `services/terraform-mcp/` | 공식 고정 Image, 조회 allowlist, 고정 stdio 런처, metadata 차단 |
| `packages/terraform-aws-s3-standard/` | 게시할 S3 Module 원본 |
| `packages/aws-ai-demo/templates/` | 실제 Registry Source/Version을 담는 Root 템플릿 |
| `packages/terraform-demo-policies/` | Sentinel hard-mandatory 및 Mock |
| `tests/local-module/` | Registry/계정 없이 검증하는 별도 Root |
| `client-configs/` | Codex CLI/IDE TOML, SSH over SSM 예시 |
| `scripts/validate-phase1.sh` | 정적 검사와 네트워크 없는 Mock 테스트만 수행 |
| `docs/`, `reports/` | 한국어 운영 절차, 근거, 제한과 검증 결과 |

문서는 [사전 요구사항](docs/00-prerequisites.md) → [검증](docs/01-code-validation.md) → [휴대폰 AWS 준비](docs/02-mobile-aws-setup.md) → [Registry/Workspace](docs/03-registry-and-workspace.md) → [MCP 연결](docs/04-mcp-connection.md) → [시연](docs/05-demo-and-recording.md) → [정리](docs/06-cleanup.md) 순서입니다.

CI는 `pull_request`와 수동 검증만 실행하며 AWS/HCP 자격증명, 자동 Plan/Apply, Tag 게시 기능이 없습니다. `install-mcp-host.sh`, `inject-mcp-token.py`, MCP Live Probe는 **승인된 Phase 2에서만** 사용합니다. 현재 Phase 1 검증은 이를 호출하지 않습니다.
