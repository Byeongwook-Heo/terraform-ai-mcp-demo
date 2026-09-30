# 표준 S3 Module

Input은 `bucket_name`(string, 필수)과 `tags`(map(string), 기본 {})입니다. Bucket, Public Access Block 네 설정, Enabled Versioning을 생성합니다. ManagedBy=Terraform은 입력으로 덮어쓸 수 없고 force_destroy=false입니다. Output은 bucket_id와 bucket_arn입니다.

Owner는 Module validation으로 검사하지 않습니다. Owner가 없거나 빈 문자열이어도 Mock Plan이 가능하며 Sentinel이 이를 차단합니다. 실제 S3 Bucket 이름의 모든 예약 패턴·전역 고유성은 AWS 배포 전에 담당자가 확인합니다.

`tests/standard.tftest.hcl`은 Mock Provider + command=plan만 사용합니다. 검증은 준비 저장소의 `scripts/validate-phase1.sh`로 수행합니다. 이 Module은 아직 Private Registry에 게시하지 않았습니다. 게시 저장소 루트로 파일과 필요한 AGENTS.md를 옮기고 Version Tag 게시를 별도 승인받으세요.
