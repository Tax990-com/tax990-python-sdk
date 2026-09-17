import hashlib
import hmac
import json
import os

from tax990 import verify_webhook_signature

WEBHOOK_SECRET = os.environ.get("TAX990_WEBHOOK_SECRET", "your-webhook-secret")


def handle_webhook(raw_body: str, signature_header: str) -> None:
    is_valid = verify_webhook_signature(
        secret=WEBHOOK_SECRET,
        payload=raw_body,
        signature=signature_header,
    )

    if not is_valid:
        print("Invalid webhook signature - rejecting")
        return

    event = json.loads(raw_body)
    print(f"Verified webhook event: {event}")


sample_payload = json.dumps(
    {
        "event": "form990n.status_changed",
        "submissionId": "sub-001",
        "status": "Accepted",
    }
)

signature = hmac.new(
    WEBHOOK_SECRET.encode(), sample_payload.encode(), hashlib.sha256
).hexdigest()

handle_webhook(sample_payload, signature)
