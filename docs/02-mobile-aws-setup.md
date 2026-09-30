# 휴대폰의 AWS 준비 — Phase 2 승인 후

이 문서의 외부 변경은 아직 실행하지 않았습니다. 휴대폰 Console에서는 코드와 보고서를 검토하고 Region, VPC/Subnet, AMI, egress, 비용과 State 방식을 먼저 확정합니다. 브라우저 호환성은 실제 기기에서 확인해야 합니다.

1. AWS Console에 SSO/MFA로 로그인해 account ID와 `ap-northeast-2` 사용 승인을 확인합니다.
2. 기존 VPC/Subnet의 Route Table, DNS, NACL, 가용 IP와 AL2023 x86_64 AMI를 확인합니다. Private Subnet이면 기존 NAT/승인 proxy가 있어야 합니다. SSM용 endpoint만으로 Docker Hub와 HCP 인터넷 접근이 해결되지는 않습니다.
3. `infra/mcp-host/terraform.tfvars.example`의 비민감 값을 준비합니다. 기본 Public IP와 Inbound는 없습니다. Public Subnet+IGW 사용은 별도 비용/접근 검토 후 `associate_public_ip_address=true`로 명시합니다.
4. 검토한 코드를 CloudShell 등 승인된 CLI에서 가져옵니다. CloudShell은 임시 관리 CLI입니다. MCP 상시 서버나 유일한 State 저장소로 사용하지 않습니다. 중요한 State는 승인된 암호화·잠금·백업 저장소로 관리합니다. 이 저장소에는 Backend 생성 코드나 자동 배포 명령이 없습니다.
5. Phase 2 승인을 받은 담당자가 별도로 검토한 인프라 변경을 수행합니다. EC2를 SSM Managed node에서 찾고 Console의 **Connect → Session Manager**를 엽니다. 접속 실패 시 Agent/Profile/egress/endpoint부터 확인하며 SSH를 전체 인터넷에 열지 않습니다.
6. SSM 관리 Shell에서 아래 상태를 확인합니다. AL2023 Agent가 없으면 bootstrap은 실패하도록 작성되어 있습니다.

```bash
sudo systemctl status amazon-ssm-agent docker --no-pager
sudo journalctl -u amazon-ssm-agent -u docker -n 50 --no-pager
sudo tail -n 50 /var/log/cloud-init-output.log
```

`user_data`는 Docker/Python/iptables 설치와 SSM Agent 활성화만 수행합니다. HCP Token이나 SSH Private Key는 포함하지 않습니다. Package 설치 시점의 AL2023 repository를 사용하므로 Phase 2에서 실제 Docker/SSM package 버전을 기록합니다.

승인된 저장소 코드를 EC2에 가져온 뒤 공개 ed25519 key 파일만 전달하고 아래 설치 스크립트를 실행합니다. 공개 key는 Client 담당자가 생성하고 Private Key는 Client의 안전한 저장소에 보관합니다.

```bash
sudo bash scripts/install-mcp-host.sh /approved/path/demo-client.pub
sudo /usr/bin/python3 scripts/inject-mcp-token.py
sudo systemctl status mcp-network-guard --no-pager
sudo journalctl -u mcp-network-guard -n 30 --no-pager
```

설치 전에 기존 `mcp-client`, home, sudoers, `mcp-isolated` 네트워크가 이 데모의 전용 대상인지 확인합니다. 운영 계정을 재사용하지 않습니다. Docker bridge `172.30.240.0/24`가 VPC·Client 경로와 충돌하면 먼저 설계를 수정하고 관련 코드·검사를 함께 갱신합니다. 이 스크립트를 다른 운영 호스트에 실행하지 않습니다.

기본 SG egress는 IPv4 TCP 443입니다. SSM `ssm`, `ssmmessages`, 해당 Region/Agent에서 필요한 `ec2messages` endpoint와 AL2023 package, Docker registry/CDN, `app.terraform.io`에 연결되어야 합니다. VPC DNS/Resolver와 시간 동기화, HTTPS 인증서도 확인합니다. 일반 DNS 서버나 별도 proxy port를 쓰면 검토한 egress를 추가해야 하며 기본 코드가 임의로 개방하지 않습니다. IPv6 또는 인터넷 전체 SSH Inbound는 추가하지 않습니다.

`client-configs/iam-ssm-operator.json.example`와 `iam-ssm-client.json.example`은 사람 관리와 시연 SSH 터널 권한 예시입니다. 각각 실제 Region/account/instance/document/session prefix로 교체하고 별도 IAM Role에 검토해 연결합니다. 브라우저 SSM Role은 호스트 관리 권한이며 AI Client에 제공하지 않습니다. Instance Profile의 SSM 권한은 접속 사용자의 IAM 권한을 대신하지 않습니다.
