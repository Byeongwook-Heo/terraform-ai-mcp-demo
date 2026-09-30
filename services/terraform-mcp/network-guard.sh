#!/usr/bin/env bash
set -euo pipefail
[[ $EUID -eq 0 && $# -eq 0 ]] || exit 2
if ! /usr/bin/docker network inspect mcp-isolated >/dev/null 2>&1; then
  /usr/bin/docker network create --driver bridge --subnet 172.30.240.0/24 \
    --opt com.docker.network.bridge.name=mcp0 mcp-isolated >/dev/null
fi
# Docker bridge에서 EC2 metadata와 link-local을 차단합니다.
/usr/sbin/iptables -C DOCKER-USER -s 172.30.240.0/24 -d 169.254.0.0/16 -j REJECT 2>/dev/null || \
  /usr/sbin/iptables -I DOCKER-USER 1 -s 172.30.240.0/24 -d 169.254.0.0/16 -j REJECT
# Docker bridge에서 호스트의 TCP 서비스/관리 소켓 접근을 차단합니다.
/usr/sbin/iptables -C INPUT -i mcp0 -j REJECT 2>/dev/null || \
  /usr/sbin/iptables -I INPUT 1 -i mcp0 -j REJECT
