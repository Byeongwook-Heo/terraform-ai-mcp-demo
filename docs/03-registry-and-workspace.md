# Registry, Workspace, OIDC, Policy 게시 — Phase 2 승인 후

## 게시 단위

준비 저장소의 `packages/terraform-aws-s3-standard`를 승인된 `terraform-aws-s3-standard` 게시 저장소의 루트로 옮깁니다. README, variables, outputs, tests와 필요한 AGENTS.md를 포함합니다. `packages/aws-ai-demo`는 Root 템플릿이며, 별도로 렌더링한 결과를 승인된 `aws-ai-demo` 저장소에 게시합니다. Policy package는 `terraform-demo-policies` 저장소의 루트로 옮깁니다. 상위 준비 저장소의 AGENTS.md가 별도 저장소에 자동 적용되지는 않습니다.

Organization 관리 담당자가 VCS 연결, Private Registry 게시 권한과 Module 이름 `s3-standard/aws`를 확인합니다. 제안 Version `1.0.0`은 **아직 게시되지 않았습니다**. Repo 생성, semantic version Tag 게시, Registry 등록은 별도 승인 후 수행합니다. HCP Registry가 표시하는 실제 Source와 Version을 기록합니다.

```bash
# 로컬 파일 생성만 수행하며 외부 호출은 없습니다.
python3 scripts/render-registry-root.py --organization ACTUAL_ORGANIZATION --output /tmp/review-registry-root
```

렌더링 결과는 `app.terraform.io/ACTUAL_ORGANIZATION/s3-standard/aws`, `version = "1.0.0"`입니다. 실제 Registry 및 MCP 응답이 이 값과 일치하는지 담당자가 확인하고 필요 시 Root의 source/version만 수정합니다. Module Source/Version은 Terraform 변수로 대체할 수 없어 템플릿으로 분리했습니다. Source를 local로 바꾼 결과를 최종 Private Registry 시연으로 사용하지 않습니다.

## Workspace

정확한 Organization/Project/Workspace 이름으로 `aws-ai-demo` VCS Workspace를 준비하고 게시 Root 디렉터리를 연결합니다. 준비 저장소 전체나 `tests/local-module`을 최종 시연 Workspace에 연결하지 않습니다. Remote execution, Terraform 1.13.5, PR Speculative Plan 활성화와 VCS branch/working directory를 확인합니다. **Auto-apply는 끄고**, Apply 담당자 권한과 branch protection/CODEOWNERS 리뷰를 설정합니다. Root에는 AWS Key 및 provider Owner default_tags를 넣지 않습니다.

`bucket_name`과 `aws_region`은 Terraform 변수로 입력합니다. HCP 환경변수는 다음 네 개입니다. Role ARN은 비민감 값이며 실제 승인된 결과를 사용합니다.

| 환경변수 | 값 |
|---|---|
| `TFC_AWS_PROVIDER_AUTH` | `true` |
| `TFC_AWS_WORKLOAD_IDENTITY_AUDIENCE` | 승인된 audience (기본 `aws.workload.identity`) |
| `TFC_AWS_PLAN_ROLE_ARN` | OIDC Plan Role ARN |
| `TFC_AWS_APPLY_ROLE_ARN` | OIDC Apply Role ARN |

`TFC_AWS_RUN_ROLE_ARN` fallback에 의존하지 않습니다. AWS Access Key/Secret Key 또는 다른 공유 AWS 변수·Variable Set이 인증을 덮어쓰지 않는지 확인합니다. AWS Provider는 Region만 설정하며 HCP의 동적 자격증명을 사용합니다.

## OIDC와 IAM

`infra/hcp-aws-identity`는 `StringEquals`로 audience와 전체 subject를 제한합니다. subject는 `organization:...:project:...:workspace:...:run_phase:plan` 또는 `...:apply`입니다. Project 이름 변경도 Trust 갱신 대상입니다. IAM Role의 trust가 토큰의 모든 조건을 묶어 검사하며 AWS가 각각을 별도 claim으로 취급한다고 가정하지 않습니다.

기존 `app.terraform.io` OIDC Provider가 있으면 `create_oidc_provider=false`와 기존 ARN을 입력합니다. 이 구성은 기존 Provider의 client ID/설정/State를 변경하지 않습니다. audience 등록 및 TLS thumbprint 적합성은 담당자가 확인합니다. 기본값은 기존 Provider가 없어도 자동 생성하지 않습니다. 없음을 확인하고 승인한 경우에만 새 생성을 선택합니다. 기존 Provider를 이 Root의 관리 대상으로 이전하려면 별도 State/Import 변경 승인과 소유권 조정이 필요하며 이번 작업에서는 import하지 않습니다.

`docs/07-permissions.md`에 Provider 소스에서 확인한 IAM 작업과 실제 검증되지 않은 권한을 구분했습니다. 권한이 부족하면 CloudTrail/API 실패 증거에 따라 필요한 exact action을 리뷰합니다. `s3:*`나 Resource `*`로 해결하지 않습니다.

## Sentinel Policy Set

Sentinel entitlement는 미확인입니다. 계약/Organization에서 실제 사용 가능 여부를 담당자가 확인하기 전까지 HCP Policy 연동은 BLOCKED입니다. 로컬 CLI Mock 성공은 entitlement 증거가 아닙니다.

승인된 Policy 저장소와 `sentinel.hcl`을 Policy Set에 연결하고 정확한 데모 Workspace에만 적용합니다. 전역 Policy Set 적용으로 고객/기존 Workspace에 영향을 주지 않습니다. `require-owner`의 enforcement level이 `hard-mandatory`인지 확인하고, Policy Set Override 허용 설정 및 담당 Team/사용자의 policy override/update 권한을 확인합니다. hard-mandatory 정책은 run override로 통과시키지 않으며 실패 Run을 Apply할 수 없어야 합니다. 조직에서 지원하는 Override UI/권한의 정확한 형태는 실제 화면/API로 검증합니다.

Owner 누락 PR에서 **Plan 성공 + Policy 실패**, Root만 수정한 후 **Policy 통과**를 실제로 확인합니다. Policy 파일/Mock/Module을 수정해 우회하지 않습니다. 통과한 Speculative Run은 Apply 대상이 아니며 Merge 후 새 Standard Run에서 다시 검사합니다.
