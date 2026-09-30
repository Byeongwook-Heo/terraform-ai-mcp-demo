# 시연 순서와 녹화

화면에는 **HCP Terraform**, Demo AWS 환경, Terraform/AWS Provider/MCP 버전을 표시합니다. TFE 호환성이나 고객 환경 배포로 소개하지 않습니다. 실제 계정 조회 전 단계는 이번 Phase 1의 코드/Mock 결과입니다.

| 순서 | 화면/행동 | 확인 증거 |
|---|---|---|
| 1 | 시연 Client에서 Private Module 검색·상세 MCP 호출 | initialize/tools/list/tools/call 및 실제 Source/Version/Input |
| 2 | AI가 조회 결과로 Registry Root 작성 | source와 version이 실제 Module과 일치 |
| 3 | 정상 Root에서 Owner 누락 patch를 적용한 작업 Branch PR | diff가 Root main.tf만 수정 |
| 4 | Speculative Plan | Plan 성공, S3/Public Access Block/Versioning 계획 |
| 5 | Sentinel Policy 검사 | Owner 누락으로 hard-mandatory 실패 |
| 6 | AI가 실패 내용을 보고 fix patch로 Owner 복구 | Module/Policy 변경 없이 Root만 수정 |
| 7 | 새 PR revision의 Plan/Policy | Policy 통과 |
| 8 | 담당자 리뷰 및 Merge | 리뷰, branch protection, Merge 증거 |
| 9 | Merge 후 새로운 Standard Run | 새 Run ID와 Plan/Policy 재검사 |
| 10 | Auto-apply 꺼진 승인 대기 | 담당자가 승인하지 않은 상태 |
| 11 | 별도 Apply 승인 후 실행 | Apply 담당자, Run ID, AWS 확인 |

렌더링한 Root fixture를 재현하는 로컬 파일 명령은 다음과 같습니다. 파일 수정뿐이며 Terraform Run을 실행하지 않습니다.

```bash
cd /path/to/rendered-root
git apply /path/to/preparation/packages/aws-ai-demo/fixtures/missing-owner.patch
# AI 수정 예시: 실패 revision에서 Owner만 추가
git apply /path/to/preparation/packages/aws-ai-demo/fixtures/fix-owner.patch
```

정상/누락/수정 fixture는 `tests/local-module/fixtures`에도 있으며 Mock plan 입력 재현용입니다. 최종 시연에는 local module harness를 사용하지 않습니다. Speculative Plan은 Apply할 수 없으며 PR Merge 승인과 AWS Apply 승인은 별개입니다.

Policy 오류를 담당자가 AI에 복사했다면 화면과 설명에 수동 전달이라고 표시합니다. 현재 allowlist는 Plan log나 Policy evaluation 전용 Tool을 포함하지 않으므로 자동 실패 내용 수집을 보장하지 않습니다. 필요한 정보를 `get_run_details`가 제공하는지는 선택 버전/실제 HCP 응답에서 확인하고, 추가 Tool이 필요하면 최소권한 리뷰 후 변경합니다.

녹화에는 조직 식별자/Token/SSH key/환경변수/State 원문이 보이지 않도록 합니다. 필수 포인트는 실제 Private Source, PR diff, Plan 성공+Policy 실패, Root만 수정된 diff, Policy 통과, 리뷰·Merge, 별도 Standard Run, 수동 Apply 승인 대기입니다. 실제 Apply 장면은 추가 승인이 있는 Phase 3에서만 촬영합니다.

재시연은 동일 Bucket을 무조건 새로 생성하지 않습니다. 이미 관리되는 State와 Bucket이 있으면 Tag 수정 시나리오로 반복하고, 대상 이름/State/Run을 확인합니다. S3에는 Object를 넣지 않습니다. Versioning Bucket에 Object가 있으면 정리 비용과 절차가 달라집니다.
