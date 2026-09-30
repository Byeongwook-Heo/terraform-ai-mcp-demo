# 계정 없는 코드 검증

검증은 임시 복사본에서 실행합니다. `init -backend=false`는 공개 Provider 설치이며 AWS/HCP 계정 조회가 아닙니다. 기존 HOME, AWS/HCP 환경변수, Terraform 인증 파일을 전달하지 않습니다. 인증 정보가 없는 공개 다운로드 proxy만 허용합니다.

```bash
# Linux x86_64 검증 환경에서만 실행
bash scripts/install-validation-tools.sh
# 출력된 venv/bin을 PATH에 추가한 후
bash scripts/validate-phase1.sh
```

설치 경로는 매번 생성하는 임시 venv이며 납품물에 포함하지 않습니다. Terraform/Sentinel zip은 공식 SHA256SUMS와 대조합니다. ShellCheck 0.10.0도 공식 release asset와 고정 SHA256으로 설치하므로 Cloud에 미리 설치되어 있을 필요가 없습니다. checksum 검사는 서명자 identity 검증과 별도이며 Provider init의 HashiCorp 서명 검증도 따로 기록합니다.

1. HCL parser가 모든 테스트를 검사합니다. `mock_provider "aws" {}`와 명시적 `command = plan`만 허용합니다. 실 Provider override, 기본 apply, provisioner, data source, 외부 Module, Backend/Cloud 블록을 차단합니다.
2. Terraform fmt와 각 검증 Root의 init/validate를 실행합니다.
3. Terraform 테스트는 **Docker --network=none**에서 실행합니다. 담당자 환경변수와 Docker socket은 컨테이너에 전달하지 않으며 임시 복사본만 mount합니다.
4. Sentinel은 로컬 `tfplan/v2` Mock만 사용합니다. Owner 누락/빈 문자열/공백/null/unknown, 무관한 resource, data resource, 순수 삭제, replacement, no-op을 검사합니다.
5. Shell 문법 및 ShellCheck, TOML/JSON 파싱, Secret 패턴, 런처 Token 파일 권한, allowlist 확장 거부, Root patch 복구를 검사합니다.
6. 공식 MCP Image를 네트워크 없는 namespace에서 실행해 initialize/tools/list/허용 외 tools/call 차단과 Module 검색/상세 조회를 확인합니다. loopback Mock API의 fixture로 Version/Input/Output을 검사합니다. 실제 Token과 Private Module 데이터가 없습니다.
7. Registry Root 태그를 fixture plan 데이터로 만들어 Sentinel CLI의 정상/누락/수정 흐름을 평가합니다. Root만 수정되고 정책 원본은 유지돼야 합니다.
8. 입력 생성기와 게시 ZIP의 allowlist, Secret/symlink 차단, SHA256 재현성을 검사합니다.

MCP는 HCP client 초기화가 완료되어야 6개 조회 도구를 등록합니다. Offline fixture에 사용하는 `offline-fixture-not-a-credential`은 인증 정보가 아닌 고정 테스트 문자열입니다. 운영 런처는 Token **값을 argv에 전달하지 않으며**, 이 offline 예시는 운영 주입 방식이 아닙니다.

`reports/validation-results.json`은 PASS/FAIL/SKIPPED/BLOCKED를 기록하고 `reports/validation-logs/`는 계정 없는 검사 출력을 보관합니다. FAIL은 exit 1, 누락/차단은 exit 2입니다. 도구가 없거나 Docker 격리가 불가능하면 성공으로 처리하지 않습니다.

활성 Root 네 곳은 `infra/mcp-host`, `infra/hcp-aws-identity`, `packages/terraform-aws-s3-standard`, `tests/local-module`입니다. 최종 Registry 템플릿은 실제 Source와 게시·Token이 없으므로 init/validate 대상에서 제외합니다. 렌더링과 patch 검사는 별도로 수행하며 실제 Registry 성공으로 표시하지 않습니다.

CI는 검증만 실행합니다. Runner에서 MCP runtime Image와 Python Mock runtime Image, Terraform test Image를 공개 registry에서 받아야 합니다. 현재 검증 완료는 CI 서버에서 실제 workflow를 실행한 증거와 다릅니다.

## 기존 Cloud 증거를 보존하는 로컬 실행

Python 3.11 이상과 requirements-validation.txt 의존성이 필요합니다. 새 결과 경로를 지정하면 기존 reports의 Cloud 로그를 보존합니다. 존재하는 경로는 덮어쓰지 않습니다.

```bash
bash scripts/validate-phase1.sh --reports-dir reports/my-local-validation
```

도구가 없으면 SKIPPED/BLOCKED와 종료 코드 2로 기록됩니다. Docker 없이 Mock Plan 또는 MCP 프로토콜 성공을 주장하지 않습니다.
