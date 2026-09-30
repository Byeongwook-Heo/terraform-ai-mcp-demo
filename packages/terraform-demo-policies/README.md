# Owner Tag Sentinel Policy

`tfplan/v2`의 관리 대상 aws_s3_bucket에 비어 있지 않은 Owner를 요구합니다. tags_all을 우선 사용하며 tags로 fallback합니다. null/공백/unknown Owner는 거부합니다. 순수 삭제는 제외하되 replacement와 no-op은 검사합니다. 무관한 resource와 data resource는 제외합니다.

`sentinel.hcl`은 hard-mandatory입니다. `sentinel test -verbose`는 로컬 Mock 12개를 검사합니다. HCP entitlement/Policy Set 적용/Override 제한은 Phase 2에서 별도로 확인해야 합니다. Mock 테스트의 PASS는 예상한 false 결과가 정상적으로 검출된 경우도 포함합니다.
