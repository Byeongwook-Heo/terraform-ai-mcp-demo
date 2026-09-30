"""출력하지 않고 검사하는 공통 Secret 패턴."""
import re

PATTERNS = [
    r"(?:AKIA|ASIA)[A-Z0-9]{16}",
    r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
    r"gh[pousr]_[A-Za-z0-9]{30,}",
    r"(?m)^\s*(?:TFE_TOKEN|AWS_SECRET_ACCESS_KEY)\s*=\s*['\"]?[^\s#'\"]+",
]


def possible_secret(text):
    return any(re.search(pattern, text) for pattern in PATTERNS)
