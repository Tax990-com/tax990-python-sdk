from __future__ import annotations

import hashlib
import hmac
import json

WEBHOOK_SECRET = "test-webhook-secret-key"

WEBHOOK_PAYLOAD = json.dumps(
    {
        "event": "filing.accepted",
        "submissionId": "submission-uuid-456",
        "recordId": "record-uuid-789",
        "timestamp": "2024-01-15T12:00:00.000Z",
    }
)


def compute_signature(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
