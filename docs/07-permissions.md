# 권한 근거와 미검증 범위

AWS Provider **6.14.1**의 `internal/service/s3/bucket.go`, `bucket_public_access_block.go`, `bucket_versioning.go`, `tags.go`를 확인했습니다. Mock는 실제 IAM 허용 여부를 검증하지 않습니다.

| 목적 | IAM Action | 소스/API 근거 |
|---|---|---|
| 존재/Region 조회 | `s3:ListBucket`, `s3:GetBucketLocation` | HeadBucket / Bucket Region |
| Tag 조회/갱신 | `s3:GetBucketTagging`, `s3:PutBucketTagging` | Get/Put/DeleteBucketTagging |
| Bucket refresh | `s3:GetBucketPolicy`, `s3:GetBucketAcl`, `s3:GetBucketCors`, `s3:GetBucketWebsite`, `s3:GetBucketLogging`, `s3:GetLifecycleConfiguration` | aws_s3_bucket의 refresh 경로 |
| 추가 refresh | `s3:GetAccelerateConfiguration`, `s3:GetBucketRequestPayment`, `s3:GetReplicationConfiguration`, `s3:GetEncryptionConfiguration`, `s3:GetBucketObjectLockConfiguration` | 동일 refresh 경로 |
| Versioning | `s3:GetBucketVersioning`, `s3:PutBucketVersioning` | 별도 Versioning resource |
| Public Access Block | `s3:GetBucketPublicAccessBlock`, `s3:PutBucketPublicAccessBlock` | Get/Put/DeletePublicAccessBlock |
| 생성/빈 Bucket 정리 | `s3:CreateBucket`, `s3:DeleteBucket` | Bucket create/delete |

`DeleteBucketTagging` API는 IAM `s3:PutBucketTagging`을 요구하고 `DeletePublicAccessBlock` API도 `s3:PutBucketPublicAccessBlock`을 요구합니다. API 이름을 그대로 IAM Action으로 만들어 넣지 않았습니다. `sts:GetCallerIdentity`는 IAM Allow가 필요하지 않은 식별 호출이므로 별도 wildcard Statement를 추가하지 않았습니다.

Plan Role은 조회 목록만, Apply Role은 조회+변경 목록을 **정확한 Bucket ARN 하나**에 허용합니다. Bucket Object ARN, `s3:*`, `s3:ListAllMyBuckets`, Object 쓰기/삭제, IAM 변경 권한은 없습니다. CreateBucket의 Owner tag 조건을 요구하지 않아 Owner 누락은 Sentinel에서 실패합니다. IAM Role은 Tag 정책의 대체 통제가 아니며 승인된 HCP Workspace 경계를 신뢰합니다.

아직 확인하지 않은 항목은 실제 HCP OIDC claim/AssumeRole, 기존 Provider audience/인증서 신뢰, 실제 Provider refresh/API 재시도 권한, 계정 SCP/Permission Boundary/KMS/Region 제약, S3 기존 객체·외부 설정, SSM login/session 접두어 및 문서 ARN, 실제 HCP Token/Team 권한 단위입니다. Provider 업데이트나 Module 리소스 추가 시 IAM 목록을 다시 리뷰합니다.

호스트 Instance Profile에는 AWS 관리형 `AmazonSSMManagedInstanceCore`만 연결합니다. 관리형 정책의 `Resource=*` 일부 작업은 Agent 기능에 필요하지만 데모 S3 배포 Role과 별개입니다. 실제 계정의 보안 기준에 따라 더 제한된 SSM 정책을 검토할 수 있습니다. 사람의 접속 IAM 예시는 ARN placeholder를 사용하며 실행 권한 생성 코드가 아닙니다.

Policy 적용/Override 설정 변경 담당자는 MCP Token과 분리합니다. Workspace run·apply 담당자, Git 리뷰 담당자, Policy 관리자 권한이 중복되면 데모의 승인 경계가 약해질 수 있으므로 실제 조직에서 확인합니다.
