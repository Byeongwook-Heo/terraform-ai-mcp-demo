# 공식 근거와 선택 버전

확인일: **2026-09-30 UTC**. 공개 문서·공식 Git tag/source·공식 Image만 확인했습니다. 계정에 인증해 조회한 AWS/HCP 정보는 없습니다. 현재 web 문서는 변경될 수 있으므로 Phase 2에서 선택 버전 및 실제 entitlement를 재확인합니다.

## 선택 버전

| 구성 | 선택 | 확인·선택 근거 |
|---|---|---|
| Terraform CLI | 1.13.5 (`>=1.13.5,<1.14.0`) | 공식 release zip/SHA256, 실제 fmt/init/validate/Mock test. 검증된 고정 기준이며 최신 버전 주장 아님 |
| AWS Provider | 6.14.1 (exact) | init 시 HashiCorp 서명 확인, lockfile 네 개, 공식 tag 소스의 S3/SSM/OIDC schema 검토 |
| Terraform MCP | 1.3.0 | 공식 tag와 이미지 --version/--help, 실제 offline initialize/tools/list/allowlist 거부 |
| Sentinel CLI | 0.40.0 | 공식 release zip/SHA256, 12개 로컬 Mock 통과. HCP entitlement와 별개 |
| Python validation | 실제 3.12 / 최소 3.11 | tomllib와 Python HCL parser 사용 |
| python-hcl2 / lark / regex | 7.3.1 / 1.3.1 / 2026.9.29 | 격리 설치, HCL 구조 preflight에 사용 |
| ShellCheck | 0.10.0 | 공식 공개 release binary, --version 및 실제 검사. 별도 서명 검증은 하지 않음 |
| Docker/Git | 환경의 28.4.0 / 2.52.0 | CLI+daemon, git --version 실확인. EC2 설치 버전은 아직 미확인 |
| actions/checkout | v5.0.0, commit 08c6903cd8c0fde910a37f88322edcfb5dd907a8 | 공식 tag ls-remote 대조; persist-credentials=false |

Terraform zip SHA256: `0dbe3fcc268eb670801af6a6456799d1ae26e72e73797f6c6167e18aafd1fd9a`

Sentinel zip SHA256: `a358aa14abfe93e7d48095e740454f026c81e8c81503010a1a58d21788179425`

고정 Image:

- `hashicorp/terraform-mcp-server:1.3.0@sha256:423a6b8e2ee06affcf090892f40c86469caba45fd2448ffa8ca5d717a174f7d5`
- 격리 Mock test runtime: `hashicorp/terraform:1.13.5@sha256:6bbb82d575aa7bd4f0a2c6e3a0838ab9590426c08a71d7a2783643f01004d356`
- 계정 없는 loopback Mock runtime: `python:3.12.12-alpine@sha256:2d91681153dd4b8cdb52d4fd34a17b9edbafa4dd3086143cfd4b6c3a84c1acb0`

MCP Git tag commit: `943a44eb28dc58432b34efdf08f7fc846adc446d`. AWS Provider tag commit: `85bbaaa527eb16fc2ac72f8b676c8a1fabee7ebe`. MCP release 이미지 USER는 65532:65532이고 stdio, --tools, error logging을 확인했습니다. tools/list의 실제 6개 이름과 required arguments는 `validation-logs/mcp-offline-protocol.txt`에 기록했습니다.

## 확인한 공식 문서

| URL | 확인 범위 |
|---|---|
| https://github.com/hashicorp/terraform-mcp-server/releases | 공개 release 페이지 및 tag 목록 접근 |
| https://github.com/hashicorp/terraform-mcp-server/tree/v1.3.0 | tagged README, init/main, toolsets, dynamic registration, tfe client, Dockerfile, Private Module Tool schema |
| https://developer.hashicorp.com/terraform/mcp-server/reference | 공개 reference 접근, 선택 버전 source/--help와 함께 확인 |
| https://developers.openai.com/codex/mcp/ | Codex stdio command/args, enabled_tools, TOML과 Client/Cloud 구분 |
| https://code.visualstudio.com/docs/copilot/customization/mcp-servers | VS Code의 별도 mcp.json 공개 문서 접근 |
| https://releases.hashicorp.com/terraform/1.13.5/ | CLI zip와 SHA256SUMS |
| https://releases.hashicorp.com/sentinel/0.40.0/ | CLI zip와 SHA256SUMS |
| https://developer.hashicorp.com/terraform/language/tests/mocking | Mock Provider와 command=plan 공개 문서 접근, 실제 실행으로 검증 |
| https://github.com/hashicorp/terraform-provider-aws/tree/v6.14.1/internal/service/s3 | Bucket refresh, Public Access Block, Versioning, tags의 API 호출 검토 |
| https://github.com/hashicorp/terraform-provider-aws/blob/v6.14.1/internal/service/iam/openid_connect_provider.go | thumbprint_list Optional/Computed 확인 |
| https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials/aws-configuration | exact audience/subject와 Plan/Apply Role 환경변수 확인 |
| https://developer.hashicorp.com/terraform/cloud-docs/registry/publish-modules | Private Module 게시 공개 문서 접근. 실제 게시 미실행 |
| https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement/import-reference/tfplan-v2 | tfplan/v2 resource_changes 공개 문서 접근. Mock 데이터로 로컬 검사 |
| https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement/manage-policy-sets | Policy Set 공개 문서 접근. 실제 scope/Override 미검증 |
| https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement | enforcement 공개 문서 접근. 실제 entitlement 미확인 |
| https://developer.hashicorp.com/terraform/cloud-docs/run/ui | Run UI 공개 문서 접근. 실제 Speculative/Standard Run 미실행 |
| https://developer.hashicorp.com/sentinel/docs/imports/strings | trim_space 지원 확인 |
| https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html | SSM 준비 요건 공개 문서 접근 |
| https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-instance-profile.html | Agent/Profile 요건 공개 문서 접근 |
| https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-restrict-access.html | instance/document/session ARN 역할 확인 |
| https://docs.aws.amazon.com/systems-manager/latest/userguide/getting-started-restrict-access-examples.html | OpenDataChannel과 Session 권한 예시 확인 |
| https://docs.aws.amazon.com/systems-manager/latest/userguide/getting-started-default-session-document.html | 기본 browser Shell도 기본 문서 ARN 권한이 필요함 확인 |
| https://docs.aws.amazon.com/systems-manager/latest/userguide/getting-started-specify-session-document.html | 명시 document-name 권한 검사 확인 |
| https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-enable-ssh-connections.html | AWS-StartSSHSession ProxyCommand와 OpenDataChannel, SSH logging 제한 확인 |
| https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-options.html | IMDSv2와 hop limit 공개 문서 접근 |
| https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteBucketTagging.html | IAM PutBucketTagging으로 Delete API 수행함 확인 |
| https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeletePublicAccessBlock.html | IAM PutBucketPublicAccessBlock으로 Delete API 수행함 확인 |
| https://docs.aws.amazon.com/cloudshell/latest/userguide/limits.html | 임시 CLI 제한 공개 문서 접근 |
| https://github.com/actions/checkout/releases/tag/v5.0.0 | 공식 release 및 Git tag commit 확인 |
| https://github.com/koalaman/shellcheck/releases/tag/v0.10.0 | 공식 release asset 다운로드·버전 검사 |

## 접근 실패와 한계

- GitHub REST API의 release endpoint는 HTTP 403으로 실패했습니다. 인증 Token을 요청하지 않고 공식 공개 Git tag, clone, release HTML과 Image로 확인했습니다.
- 일부 raw.githubusercontent.com URL은 HTTP 404였습니다. 공식 tag clone으로 해당 source를 읽었습니다.
- AWS service authorization index URL은 HTTP 200이나 본문이 이동/redirect shell인 범위만 확인했습니다. IAM action 근거는 Provider 소스와 개별 AWS API 문서로 보완했고, 실제 IAM 허용 여부는 검증하지 않았습니다.
- 초기 Terraform 다운로드는 proxy를 제거하면 연결이 거부되었습니다. 인증 없는 공개 proxy만 격리 환경에 허용하자 init이 성공했습니다. proxy 값이나 자격증명은 기록하지 않았습니다.
- HCP Token 권한/entitlement, 기존 OIDC, AMI와 Docker host firewall은 공개 문서만으로 실제 환경 적합성을 확정할 수 없습니다. Phase 2 확인 목록에 남겼습니다.

## 후속 Cloud 준비의 실제 확인 — 2026-09-30

- HashiCorp Terraform 1.13.5 / Sentinel 0.40.0 공식 zip/SHA256SUMS를 다시 내려받아 설치·검증했습니다. 기존 고정 버전과 Image digest를 유지했습니다.
- ShellCheck 공식 v0.10.0 Linux x86_64 release asset를 다시 받아 SHA256 `6c881ab0698e4e6ea235245f22832860544f17ba386442fe7e9d629f8cbedf87`을 확인하고 설치 스크립트에 고정했습니다. 별도 서명자 검증은 수행하지 않았습니다.
- https://github.com/hashicorp/terraform-mcp-server/tree/v1.3.0 를 clone하여 `search_private_modules`와 `get_private_module_details`의 입력과 응답 생성을 확인했습니다. Commit `943a44eb28dc58432b34efdf08f7fc846adc446d`입니다.
- https://github.com/hashicorp/go-tfe/tree/v1.110.0 를 clone하여 Module list/read와 `/api/registry/v1/modules/...`의 JSON/JSON:API schema를 확인했습니다. Commit `908c574bd976e05b8d9a0429a66d3f51e8e8f673`입니다. 이 저장소 snapshot의 소스 파일은 `v1.go`였고 추측한 raw 파일 URL은 404였습니다. 실제 Clone 소스로 확인했습니다.
- https://github.com/actions/upload-artifact/releases/tag/v4.6.2 의 Git tag를 `git ls-remote`로 대조했습니다. 고정 Commit `ea165f8d65b6e75b540449e92b4886f43607fa02`입니다. CI artifact는 검증 보고서와 example 입력으로 생성한 패키지 경로만 보존합니다.
- Sentinel 0.40.0 `apply -help`, `test -help`의 실제 옵션과 정상/실패 반환 코드를 확인하고 fixture 정책 리허설을 실행했습니다. 실제 HCP 정책 또는 Registry entitlement 검증은 아닙니다.
