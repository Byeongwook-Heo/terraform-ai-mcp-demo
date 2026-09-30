"""network=none의 loopback Mock Registry. 실제 HCP 조회 결과가 아닙니다."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

MODULE = {
    "type": "registry-modules", "id": "mod-fixture-s3",
    "attributes": {
        "name": "s3-standard", "namespace": "fixture-org", "provider": "aws",
        "registry-name": "private", "no-code": False,
        "version-statuses": [{"version": "1.0.0", "status": "ok"}],
        "created-at": "2026-01-01T00:00:00Z", "updated-at": "2026-01-01T00:00:00Z",
    },
}
DETAILS = {
    "id": "fixture-org/s3-standard/aws/1.0.0", "namespace": "fixture-org",
    "name": "s3-standard", "provider": "aws", "version": "1.0.0",
    "description": "격리 검증용 Module fixture; 실제 Registry 게시물 아님",
    "root": {
        "inputs": [
            {"name": "bucket_name", "type": "string", "description": "Bucket 이름", "required": True},
            {"name": "tags", "type": "map(string)", "description": "태그", "default": "{}", "required": False},
        ],
        "outputs": [{"name": "bucket_id", "description": "Bucket ID"}, {"name": "bucket_arn", "description": "Bucket ARN"}],
        "provider_dependencies": [{"name": "aws", "namespace": "hashicorp", "source": "hashicorp/aws", "version": "6.14.1"}],
    },
}


def response_for(path):
    path = urlsplit(path).path
    if path == "/api/v2/organizations/fixture-org/registry-modules":
        return {"data": [MODULE], "meta": {"pagination": {"current-page": 1, "total-pages": 1, "total-count": 1}}}
    if path == "/api/v2/organizations/fixture-org/registry-modules/private/fixture-org/s3-standard/aws":
        return {"data": MODULE}
    if path == "/api/registry/v1/modules/fixture-org/s3-standard/aws/1.0.0":
        return DETAILS
    return None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/v2/ping":
            self.send_response(204)
            self.send_header("TFP-API-Version", "2.6")
            self.send_header("TFE-Version", "mock")
            self.end_headers()
            return
        body = response_for(self.path)
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        data = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.api+json" if self.path.startswith("/api/v2/") else "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        self.send_response(405)
        self.end_headers()

    do_PATCH = do_POST
    do_DELETE = do_POST

    def log_message(self, *_):
        pass

if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8081), Handler).serve_forever()
