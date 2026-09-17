from __future__ import annotations

from typing import Any


class ApiKeysResource:
    """
    API key management endpoints are not documented in the Tax990 Public API.
    Authentication uses the JWS/JWT flow — see OAuthClient.
    """

    async def create(self, options: Any) -> None:
        raise NotImplementedError(
            "API key management endpoints are not available in the Tax990 Public API. "
            "See OAuthClient for the documented authentication flow."
        )

    async def list(self) -> None:
        raise NotImplementedError(
            "API key management endpoints are not available in the Tax990 Public API."
        )

    async def revoke(self, key_id: str) -> None:
        raise NotImplementedError(
            "API key management endpoints are not available in the Tax990 Public API."
        )
