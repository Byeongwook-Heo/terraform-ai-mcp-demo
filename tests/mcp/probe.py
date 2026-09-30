#!/usr/bin/env python3
"""Offline는 network=none. Live Private 조회는 Phase 2 승인과 입력값이 필요합니다."""
import argparse
import json
import os
import queue
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "services/terraform-mcp/config.json").read_text())

class Session:
    def __init__(self, command):
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.messages = queue.Queue()
        def reader():
            for line in self.process.stdout:
                try:
                    message = json.loads(line)
                    if message.get("jsonrpc") != "2.0":
                        raise json.JSONDecodeError("not JSON-RPC", line, 0)
                    self.messages.put(message)
                except json.JSONDecodeError:
                    self.messages.put(ValueError("MCP stdout에 JSON 이외 출력이 있습니다."))
        self.reader = threading.Thread(target=reader, daemon=True)
        self.reader.start()
        self.next_id = 0
    def send(self, method, params, notification=False):
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notification:
            self.next_id += 1
            message["id"] = self.next_id
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()
        if notification:
            return None
        deadline = time.monotonic() + 30
        while True:
            response = self.messages.get(timeout=max(0.01, deadline - time.monotonic()))
            if isinstance(response, Exception):
                raise response
            if response.get("id") == message["id"]:
                return response
    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=10)
        self.reader.join(timeout=2)
        while not self.messages.empty():
            if isinstance(self.messages.get_nowait(), Exception):
                raise ValueError("MCP stdout에 JSON-RPC 이외 출력이 있습니다.")

def probe(command, query=None):
    session = Session(command)
    try:
        init = session.send("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "phase1-probe", "version": "1.0.0"}})
        if "result" not in init:
            raise ValueError("initialize에 실패했습니다.")
        session.send("notifications/initialized", {}, notification=True)
        # HCP client 등록은 initialize 후 비동기로 마무리될 수 있습니다.
        tools = []
        for _ in range(10):
            listed = session.send("tools/list", {})
            tools = listed.get("result", {}).get("tools", [])
            if tools:
                break
            time.sleep(0.2)
        if {tool["name"] for tool in tools} != set(CONFIG["tools"]):
            raise ValueError("서버 Tool allowlist가 정확히 일치하지 않습니다.")
        denied = session.send("tools/call", {"name": "create_workspace", "arguments": {}})
        if not ("error" in denied or denied.get("result", {}).get("isError")):
            raise ValueError("허용 목록 외 Tool 호출이 차단되지 않았습니다.")
        if query is not None:
            if query.get("name") not in {"search_private_modules", "get_private_module_details"}:
                raise ValueError("Private Module 조회만 허용합니다.")
            called = session.send("tools/call", query)
            if "error" in called or called.get("result", {}).get("isError"):
                raise ValueError("실제 MCP Private 조회에 실패했습니다. 결과를 공개 로그로 출력하지 마세요.")
            # 응답 원문에는 조직/Module 정보가 있어 저장하지 않습니다.
            print("PASS: live tools/call 응답. 별도로 Source/Version/Input 내용을 담당자가 확인하세요.")
        else:
            print("PASS: offline initialize + tools/list(6) + allowlist 외 tools/call 차단; 계정 조회 없음.")
        summary = {"protocolVersion": init["result"]["protocolVersion"], "serverInfo": init["result"].get("serverInfo"), "tools": [{"name": t["name"], "required": t.get("inputSchema", {}).get("required", [])} for t in tools]}
        print(json.dumps(summary, ensure_ascii=False))
    finally:
        session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--offline", action="store_true")
    mode.add_argument("--live-query", type=Path)
    parser.add_argument("--approval-reference")
    args = parser.parse_args()
    if args.offline:
        subprocess.run(["docker", "pull", "python:3.12.12-alpine@sha256:2d91681153dd4b8cdb52d4fd34a17b9edbafa4dd3086143cfd4b6c3a84c1acb0"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        helper = subprocess.check_output([
            "docker", "run", "--rm", "--detach", "--network=none", "--read-only",
            "--user=" + str(os.getuid()) + ":" + str(os.getgid()), "--cap-drop=ALL",
            "--mount", "type=bind,src=" + str(ROOT / "tests/mcp/mock_api.py") + ",dst=/mock.py,readonly",
            "python:3.12.12-alpine@sha256:2d91681153dd4b8cdb52d4fd34a17b9edbafa4dd3086143cfd4b6c3a84c1acb0", "python", "/mock.py",
        ], text=True).strip()
        command = ["docker", "run", "--rm", "--pull=never", "--network=container:" + helper, "-i", "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges", "-e", "ENABLE_TF_OPERATIONS=false", "-e", "TFE_ADDRESS=http://127.0.0.1:8081", "-e", "TFE_TOKEN=offline-fixture-not-a-credential", CONFIG["image"], "stdio", "--log-level=error", "--tools=" + ",".join(CONFIG["tools"])]
        try:
            subprocess.run(["docker", "exec", helper, "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/api/v2/ping', timeout=5).close()"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            probe(command)
        finally:
            subprocess.run(["docker", "stop", "--time=1", helper], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        if not args.approval_reference:
            parser.error("Phase 2 승인 참조가 필요합니다.")
        query = json.loads(args.live_query.read_text())
        if "REPLACE" in json.dumps(query):
            parser.error("실제 비민감 입력값으로 교체하세요.")
        # Phase 1 CI/검증 스크립트는 이 경로를 호출하지 않습니다.
        probe(["ssh", "-T", "-o", "BatchMode=yes", "terraform-mcp-ssm"], query)
