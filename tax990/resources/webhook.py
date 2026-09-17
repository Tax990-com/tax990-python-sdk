from __future__ import annotations

from typing import Any


class WebhookResource:
    """
    Webhook management endpoints are not documented in the Tax990 Public API.
    Use verify_webhook_signature() from tax990.utils to verify incoming payloads.
    """

    async def register(self, config: Any) -> None:
        raise NotImplementedError(
            "Webhook management endpoints are not available in the Tax990 Public API."
        )

    async def list(self) -> None:
        raise NotImplementedError(
            "Webhook management endpoints are not available in the Tax990 Public API."
        )

    async def revoke(self, webhook_id: str) -> None:
        raise NotImplementedError(
            "Webhook management endpoints are not available in the Tax990 Public API."
        )
