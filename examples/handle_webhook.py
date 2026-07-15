"""
Verify and handle an incoming webhook payload.

This example simulates what your web server handler would do when the
Tax990 platform POSTs a webhook event to your endpoint.

Run:
    python examples/handle_webhook.py
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os

from dotenv import load_dotenv

from tax990.models.webhook import WebhookVerifyOptions
from tax990.utils.webhook_verifier import verify_webhook_signature

load_dotenv()


def simulate_incoming_webhook() -> tuple[str, str]:
    """Builds a fake incoming payload + valid HMAC signature."""
    secret = os.environ.get("TAX990_WEBHOOK_SECRET", "example-webhook-secret")
    payload = json.dumps(
        {
            "event": "filing.accepted",
            "submissionId": "submission-uuid-456",
            "recordId": "record-uuid-789",
            "timestamp": "2024-01-15T12:00:00.000Z",
        }
    )
    signature = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return payload, signature


def handle_webhook(raw_body: str, x_signature_header: str) -> None:
    secret = os.environ.get("TAX990_WEBHOOK_SECRET", "example-webhook-secret")

    valid = verify_webhook_signature(
        WebhookVerifyOptions(
            secret=secret,
            payload=raw_body,
            signature=x_signature_header,
        )
    )

    if not valid:
        print("Webhook signature verification FAILED — reject request.")
        return

    event = json.loads(raw_body)
    print(f"Webhook verified. Event: {event['event']}")
    print(f"  Submission : {event['submissionId']}")
    print(f"  Record     : {event['recordId']}")
    print(f"  Timestamp  : {event['timestamp']}")


if __name__ == "__main__":
    payload, signature = simulate_incoming_webhook()
    print(f"Incoming payload  : {payload}")
    print(f"Incoming signature: {signature}\n")
    handle_webhook(payload, signature)
