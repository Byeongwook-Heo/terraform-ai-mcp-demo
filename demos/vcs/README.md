# GitHub PR과 TFE 정책 검증 데모

기존 [Byeongwook-Heo/terraform-ai-mcp-demo](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo) 저장소의 PR 변경안을 기존 TFE `hashicorp_lab/aws-ai-demo` Workspace에서 검증합니다. 승인 모듈은 `hashicorp_lab/s3-standard/aws` `1.0.0`입니다.

`aws-ai-demo/`의 `main.tf`, `variables.tf`, `versions.tf`는 정상 Root를 기준으로 준비했습니다. 최초 변경은 `main.tf`의 `Environment = "demo"`를 `"production"`으로 바꾼 한 줄입니다. 기존 `require-demo-environment` 정책의 차단을 확인한 뒤, 같은 PR에서 `demo`로 복구하고 다시 검증합니다. Module source·버전·리전·Owner와 기존 정책은 유지합니다.

현재 연동 경로는 **PR의 정확한 commit SHA → 운영자의 TFE API Run 발행 → 해당 commit의 GitHub status 게시**입니다. Run에 사용한 코드와 PR commit을 대조하고 Plan·정책 결과를 status로 기록합니다. 이 경로는 TFE의 native VCS webhook 연동으로 실행되는 흐름이 아닙니다.

담당자는 수정된 PR과 검증 결과를 Review한 뒤 Merge합니다. Merge 이후의 Standard Run은 별도 단계이며, 그 Run의 Plan·정책 확인과 담당자의 수동 Apply 승인은 각각 구분합니다. 이번 PR 검증은 기존 자원을 사용하는 Plan-only 범위입니다. 새 AWS 자원 생성과 Apply는 수행하지 않습니다.

자격증명·Token·State·원문 로그는 이 공개 경로에 포함하지 않습니다. 실제 Run 링크와 비민감 결과만 기록합니다.

실제 PR과 Run 링크는 PR 설명의 검증 결과에서 확인합니다.
