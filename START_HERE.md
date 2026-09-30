# 시작 방법

이 패키지는 구축용 코드가 아니라 Codex에 전달할 작업 지침이다.
AWS, HCP Terraform, GitHub에 실제 변경을 수행한 상태가 아니다.

## 사용 순서

1. Codex가 접근할 준비용 GitHub 저장소를 하나 선택하거나 만든다.
2. AGENTS.md, DEMO_SPEC.md, START_HERE.md를 저장소 루트에 넣는다.
3. 기존 AGENTS.md가 있으면 덮어쓰지 말고 기존 규칙과 병합한다.
4. Codex Cloud에서 해당 저장소를 선택하고 필요한 Terraform/Sentinel/정적검사 도구를 준비한다.
5. 아래 Phase 1 프롬프트를 보낸다.
6. 결과를 검토한 뒤 실제 배포는 별도 Phase 2 작업으로 승인한다.

AGENTS.md는 Codex의 프로젝트 지침 탐색 대상이다. DEMO_SPEC.md는 아래 프롬프트와 AGENTS.md에서 명시적으로 읽도록 연결했다.
첨부만으로 자동 배포 권한이나 실행 환경이 생기지 않는다. 파일을 읽을 수 없는 화면이라면 저장소 파일로 추가한 뒤 시작한다.

## 지금 보낼 프롬프트

```text
저장소 루트의 AGENTS.md와 DEMO_SPEC.md를 읽고,
AWS 기반 AI + Terraform MCP + Private Registry 데모의 Phase 1만 구현해줘.

나는 지금 PC가 없으므로 Codex Cloud에서 가능한 코드 작성·문서화·격리된 테스트부터 진행하고 싶다.

환경 조건:
- Terraform MCP Server는 AWS EC2의 Docker에서 실행한다.
- 초기 제어 플랫폼은 HCP Terraform이다. 기존 TFE VM과 고객 환경은 변경하지 않는다.
- 데모 리소스는 AWS S3이며 실제 Private Module을 사용한다.
- 휴대폰에서 EC2를 관리할 수 있도록 Session Manager 구성도 준비한다.
- MCP 조회 권한과 AWS 인프라 배포 권한을 분리한다.

이번 작업은 코드, 설정 템플릿, 단위 테스트, 운영 문서 작성까지다.
실제 AWS/HCP 리소스 생성·변경, terraform apply/destroy,
새 외부 저장소 생성, PR Merge, Module Tag 게시, Secret 등록은 하지 마.

계정 ID, Organization, Repo, VPC/Subnet, Token이 없더라도
미정값은 템플릿과 required-inputs.md에 남기고 나머지 작업을 진행해줘.
관리자 Token이나 장기 AWS Key는 요청하지 마.

먼저 현재 Repository 구조와 공식 문서로 구현 계획을 확인한 뒤 코드를 작성해줘.
이전 대화의 버전·명령을 그대로 신뢰하지 말고 선택 버전의 지원 여부를 검증해줘.
Docker나 네트워크가 없어서 검증하지 못한 항목은 BLOCKED/SKIPPED로 기록해줘.

마지막에 변경 파일, 실행한 검증, PASS/FAIL, 실환경 미검증 항목,
Phase 2에 필요한 값과 승인을 보고해줘.
PR 생성이 가능한 권한/환경이면 검토용 PR로 제출하되 Merge하지 마.
```

## 현재 권장 도달점

PC 없이 먼저 코드와 검증 자료를 준비한다.
AWS Console에 로그인할 수 있고 변경 범위를 승인한 다음에는 EC2/SSM, Docker 설치,
HCP Registry/Workspace, OIDC 설정 등을 별도 환경에서 진행할 수 있다.
로컬 Client→AWS MCP 연결과 실제 세미나 화면 녹화는 해당 Client가 준비된 환경에서 검증한다.

Codex Cloud 작업이 시작됐다고 AWS 리소스가 자동 생성되거나, 로컬 SSH/MCP 설정이 자동 연결되는 것은 아니다.
