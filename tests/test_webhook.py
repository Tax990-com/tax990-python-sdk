from __future__ import annotations

import pytest

from tax990.models.webhook import WebhookVerifyOptions
from tax990.resources.webhook import WebhookResource
from tax990.utils.webhook_verifier import verify_webhook_signature
from tests.fixtures.webhook_fixtures import (
    WEBHOOK_PAYLOAD,
    WEBHOOK_SECRET,
    compute_signature,
)

# ---------------------------------------------------------------------------
# verify_webhook_signature
# ---------------------------------------------------------------------------


def test_valid_signature_returns_true() -> None:
    sig = compute_signature(WEBHOOK_PAYLOAD, WEBHOOK_SECRET)
    assert verify_webhook_signature(
        WebhookVerifyOptions(
            secret=WEBHOOK_SECRET,
            payload=WEBHOOK_PAYLOAD,
            signature=sig,
        )
    ) is True


def test_tampered_payload_returns_false() -> None:
    sig = compute_signature(WEBHOOK_PAYLOAD, WEBHOOK_SECRET)
    tampered = WEBHOOK_PAYLOAD.replace("accepted", "rejected")
    assert verify_webhook_signature(
        WebhookVerifyOptions(secret=WEBHOOK_SECRET, payload=tampered, signature=sig)
    ) is False


def test_wrong_secret_returns_false() -> None:
    sig = compute_signature(WEBHOOK_PAYLOAD, WEBHOOK_SECRET)
    assert verify_webhook_signature(
        WebhookVerifyOptions(
            secret="wrong-secret",
            payload=WEBHOOK_PAYLOAD,
            signature=sig,
        )
    ) is False


def test_mismatched_length_returns_false() -> None:
    assert verify_webhook_signature(
        WebhookVerifyOptions(
            secret=WEBHOOK_SECRET,
            payload=WEBHOOK_PAYLOAD,
            signature="short",
        )
    ) is False


# ---------------------------------------------------------------------------
# WebhookResource (stub)
# ---------------------------------------------------------------------------


async def test_register_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError, match="not available"):
        await WebhookResource().register({})


async def test_list_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError, match="not available"):
        await WebhookResource().list()


async def test_revoke_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError, match="not available"):
        await WebhookResource().revoke("some-id")
