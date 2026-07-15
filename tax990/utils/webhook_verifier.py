from __future__ import annotations

import hashlib
import hmac

from tax990.models.webhook import WebhookVerifyOptions


def verify_webhook_signature(options: WebhookVerifyOptions) -> bool:
    """
    Verifies an HMAC-SHA256 webhook signature.
    Uses hmac.compare_digest for timing-safe comparison.
    """
    expected = hmac.new(
        options.secret.encode("utf-8"),
        options.payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if len(expected) != len(options.signature):
        return False

    return hmac.compare_digest(
        options.signature.encode("utf-8"),
        expected.encode("utf-8"),
    )
