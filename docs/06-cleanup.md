# 초기화, 재시작 및 정리

2026-09-30 AWS Host/Identity와 별도 S3 State Bucket을 생성했습니다. 실제 대상과 State는 [AWS 생성 후 재개](11-aws-created.md)를 확인합니다. 삭제는 아직 승인·실행하지 않았으며 State Bucket은 두 Root destroy에 포함되지 않으므로 버전·감사·복구 자료를 별도로 보존합니다.

계정 없는 검증 스크립트는 임시 Terraform 복사본, network=none 컨테이너와 Mock API를 종료·삭제하고 보고서만 남깁니다. CLI/Provider download cache와 로컬 `.terraform`은 격리 작업 환경의 임시 파일입니다.

## 승인된 EC2에서 세션 재시작

MCP는 stdio 세션 종료 시 `--rm`으로 해당 컨테이너를 정리합니다. 중단되었다면 관리 담당자가 해당 데모 컨테이너만 확인해 종료합니다. 다른 컨테이너를 대상으로 하는 전체 stop/prune 명령은 사용하지 않습니다. Guard service와 Docker 상태를 확인하고 런타임 Token을 다시 주입한 뒤 Client MCP 세션을 재시작합니다.

```bash
sudo systemctl status mcp-network-guard docker amazon-ssm-agent --no-pager
sudo journalctl -u mcp-network-guard -n 30 --no-pager
# 실제 Token 값을 출력하지 않습니다.
sudo stat -c '%U %a %F' /run/terraform-mcp/token
```

재부팅/Docker 재시작 후 iptables 차단 규칙과 bridge 설정을 다시 확인합니다. 런처는 두 차단 규칙이 없으면 시작을 거부합니다. 설치 후 실제 AL2023에서 service/규칙과 격리 컨테이너의 IMDS 차단은 확인했으나 재부팅·Docker 재시작 검증은 수행하지 않았습니다. Network guard 설치 실패를 무시하고 런처를 실행하지 않습니다.

## Phase 2/3에서만 승인할 외부 정리

1. 시연 종료 후 MCP 조회 Token을 발급자가 회수하고 세션을 닫습니다. 운영자의 별도 승인 아래 EC2의 `/run/terraform-mcp/token`과 Client key를 정리합니다. HCP Token 회수와 파일 삭제는 서로 다른 작업입니다.
2. S3 담당자가 대상 Workspace/State/Bucket을 확인하고 삭제 영향을 검토합니다. Module은 `force_destroy=false`이고 Object 삭제 권한도 없습니다. Object/Version/Delete marker가 있다면 승인된 담당자가 별도 범위로 정리하며 AI가 자동으로 강제 삭제하지 않습니다.
3. Standard Run의 삭제 Plan/Policy를 리뷰하고 별도 사람 승인 후 정리합니다. 순수 Bucket 삭제는 Owner Policy에서 제외하지만 destroy 승인·권한과 다른 Policy는 계속 필요합니다.
4. EC2/EBS/Instance Profile/전용 SG/전용 IAM Role 등 **이 데모가 생성한 리소스만** 검토한 변경으로 정리합니다. 기존 VPC/Subnet/NAT/OIDC Provider는 삭제하지 않습니다.
5. HCP Workspace/Registry Version/Policy Set/VCS 게시물은 필요한 보존 기간과 감사 증거를 검토하고 별도 승인 후 정리합니다. State 백업에는 실제 식별자가 있으므로 공개 보고서에 넣지 않습니다.

정리 리소스 목록과 비용 종료를 확인합니다. 이 저장소에는 자동 apply/destroy/import나 리소스 정리 CI가 없습니다. 검토가 끝나도 Phase 2로 자동 진행하지 않습니다.
