# MCP 연결과 프로토콜 검증

## 관리 경로와 시연 경로

휴대폰의 브라우저 Session Manager는 EC2 관리 Shell입니다. 시연 Codex stdio 연결은 별도 Client의 `ssh -T`와 **SSH over Session Manager** 경로입니다. Client에는 AWS CLI, Session Manager plugin, OpenSSH, SSO/MFA Role, ed25519 Private Key 및 검증한 host key가 필요합니다. EC2의 SSH daemon은 내부에서 실행하지만 기본 SG Inbound는 열지 않습니다.

관리 담당자가 SSM Shell에서 `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`를 확인하고 신뢰할 수 있는 경로로 Client 담당자에게 전달합니다. Host key를 실제 Instance ID alias로 known_hosts에 등록합니다. `StrictHostKeyChecking=yes`를 유지하며 무검증 ssh-keyscan 결과만 신뢰하지 않습니다. Client는 `client-configs/ssh.config.example`의 Region/Instance ID/key 경로를 수정해 필요한 Host 블록만 병합합니다.

전용 `mcp-client`는 docker 그룹에 가입하지 않으며 Root 소유 forced command가 고정 런처만 실행합니다. authorized_keys의 `restrict`는 PTY/forwarding/agent forwarding을 막습니다. Root 소유 home/키 파일을 사용하고 OS password 로그인을 비활성화해야 합니다. 공개 authorized_keys는 Root 0644로 두어 sshd의 사용자 권한으로 읽을 수 있게 하고 사용자 파일·디렉터리 쓰기는 금지합니다. Secret과 Private Key의 0600은 유지합니다. 실제 배포의 최초 읽기 실패와 수정 후 연결 증거는 [AWS 생성 결과](11-aws-created.md)에 있습니다. 해당 계정의 다른 SSH key, AuthorizedKeysCommand, 대체 인증 방식이 없는지 검토합니다. 관리자가 범용 sudo/키 쓰기 권한을 추가하면 이 경계가 무너집니다.

SSH over SSM은 암호화된 터널 내부의 명령 내용을 Session Manager가 로깅하지 못합니다. 브라우저 관리 세션 로깅과 이 터널의 감사 범위를 구분하고 CloudTrail StartSession/TerminateSession 및 SSH 접속 이벤트를 보관합니다. MCP 내용 로그에 Token이나 조직 데이터가 들어가지 않도록 별도 검토합니다.

## Image, 도구와 Token

공식 `hashicorp/terraform-mcp-server:1.3.0`을 확인한 digest `sha256:423a6b8e2ee06affcf090892f40c86469caba45fd2448ffa8ca5d717a174f7d5`와 함께 고정했습니다. EC2 설치 시 이미지 pull과 실제 `--version`/`--help`를 다시 확인합니다. x86_64를 선택했으며 다른 architecture 검증은 수행하지 않았습니다.

Server의 `--tools`와 Codex TOML의 `enabled_tools`에 다음 6개만 설정했습니다.

- `search_private_modules`
- `get_private_module_details`
- `list_workspaces`
- `list_runs`
- `get_run_details`
- `get_token_permissions`

선택 버전에서 모두 존재하는 이름입니다. `ENABLE_TF_OPERATIONS=false`도 적용하지만 이 값만으로 조회 전용이라고 판단하지 않습니다. 권한 없는 Token, HCP Team 접근, 서버 allowlist가 함께 필요합니다. upstream instruction에 다른 Tool 사용 안내가 있어도 등록된 6개 밖의 Tool은 사용할 수 없어야 합니다.

운영자는 승인된 EC2 터미널에서 `inject-mcp-token.py`로 조회 전용 Token을 숨김 입력합니다. 일반 stdin fallback은 허용하지 않습니다. 값은 `/run/terraform-mcp/token`에 Root 0600으로만 기록하며 재부팅 후 다시 주입합니다. SSH Private Key/Token을 저장소나 tfvars, user_data에 넣지 않습니다. SSM 세션 녹화/외부 terminal recorder가 입력을 수집하는 환경인지 확인하고 승인된 Secret 저장소 주입 방식을 사용할 수 있습니다. 기본 Profile에는 Secrets Manager/SSM Parameter 읽기 권한을 추가하지 않았습니다.

런처는 파일 권한·symlink·hardlink를 검사하고 Docker env로 Token을 전달합니다. argv에는 환경변수 **이름만** 있습니다. Docker 관리자/root는 컨테이너 환경과 프로세스 메모리를 읽을 수 있습니다. 이 신뢰 경계를 없애는 방식은 아니므로 관리자 수를 제한하고 Token을 짧게 발급·회수합니다. `docker inspect`, 환경 전체 출력, set -x, debug/trace 로깅 또는 원문 transcript를 수집하지 않습니다.

stdio는 Client 세션마다 컨테이너가 시작되고 종료됩니다. 인증 없는 HTTP 서비스, 공개 8080, Port publish, Docker socket mount, 상시 systemd MCP HTTP 서비스가 없습니다. `docker --log-driver=none`으로 MCP 출력의 Docker 로그 저장을 끄고 stdout에는 JSON-RPC만 전달합니다. stderr도 그대로 저장하지 말고 민감 정보를 제거한 상태로 장애 원인을 기록합니다.

## Client 설정

Codex CLI/IDE의 `~/.codex/config.toml`에 `client-configs/codex.config.toml.example`의 MCP 블록만 병합합니다. Token은 Client 설정에 없습니다. `codex mcp list`는 설정 확인이며 실제 initialize/tools/call 성공 증거가 아닙니다. 이 환경에서 Codex CLI/IDE 실제 연결은 수행하지 않았습니다.

`vscode.mcp.json.example`은 VS Code 내장 MCP용 대안 예시입니다. Codex TOML과 다른 설정 형식이며 Client allowlist UI 및 승인은 별도로 설정해야 합니다. 서버 allowlist는 그대로 유지합니다.

## Phase 1에서 검증하는 범위

```bash
python3 tests/mcp/probe.py --offline
```

로컬 Mock API와 MCP는 `network=none` namespace를 공유하며 loopback만 연결합니다. initialize, 정확한 6개 tools/list, allowlist 외 create_workspace 차단을 검사합니다. Mock API는 Module 검색/상세 fixture를 제공합니다. 실제 Private Registry 응답이 아닙니다. 이 검증은 실제 Token, HCP API 직접 조회, EC2/SSM, 실제 Private Module 조회의 성공 증거가 아닙니다.

## 승인된 Phase 2에서만 수행할 실제 조회

먼저 담당자가 동일 최소권한 Token의 직접 HCP API 조회를 별도로 확인하고 결과를 API 경로로 표기합니다. 안전한 SDK/메모리 기반 Authorization 헤더를 사용하고 Token 값을 curl argv에 넣지 않습니다. 결과를 AI에 복사한 작업은 MCP 자동 조회가 아닙니다.

실제 MCP 테스트는 initialize → notifications/initialized → tools/list → tools/call 순서입니다. `search_private_modules`의 arguments는 `terraform_org_name`, 선택 `search_query`입니다. 응답에서 실제 `private_module_id`를 확인한 뒤 `get_private_module_details`에 `terraform_org_name`, `private_module_id`, `registry_name=private`, `private_module_version`을 전달합니다.

```bash
# 별도 운영 승인 후, 비민감 query JSON의 REPLACE 값을 실제 값으로 교체
python3 tests/mcp/probe.py --live-query /approved/path/private-query.json --approval-reference APPROVED_CHANGE_REFERENCE
```

이 명령은 Phase 1 검증/CI에서 실행하지 않습니다. 실제 Source/Version/Input/Output이 준비한 Module과 일치하는지 응답 내용을 담당자가 확인합니다. 테스트 스크립트는 원문 응답을 출력·저장하지 않으므로 조직 승인에 따라 비식별 증거를 별도로 남깁니다. Tool 자체의 isError=false만으로 Module 내용 일치까지 자동 판정하지 않습니다.

HTTP 연결을 원하면 TLS와 인증, 접속 권한, proxy trust, 세션 관리·감사 설계를 새로 승인해야 합니다. 기본 구성에 자동 추가하지 않습니다.
