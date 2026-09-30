"""Network=none namespace의 loopback에서 /api/v2/ping만 모의합니다."""
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/api/v2/ping":
            self.send_response(404)
        else:
            self.send_response(204)
            self.send_header("TFP-API-Version", "2.6")
            self.send_header("TFE-Version", "mock")
        self.end_headers()
    def log_message(self, *_):
        pass

HTTPServer(("127.0.0.1", 8081), Handler).serve_forever()
