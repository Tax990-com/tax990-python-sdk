from __future__ import annotations

import asyncio
import time
from typing import Optional

from tax990.auth.oauth_client import OAuthClient
from tax990.models.auth import StoredToken

_EXPIRY_BUFFER_SECONDS = 30


class TokenManager:
    """
    Caches the access token and refreshes it automatically before expiry.
    Uses asyncio.Lock to deduplicate concurrent refresh calls.
    """

    def __init__(self, oauth_client: OAuthClient) -> None:
        self._oauth_client = oauth_client
        self._token: Optional[StoredToken] = None
        self._lock = asyncio.Lock()

    async def get_token(self) -> str:
        if self._token and not self._is_expired(self._token):
            return self._token.access_token
        async with self._lock:
            if self._token and not self._is_expired(self._token):
                return self._token.access_token
            access_token, expires_in = await self._oauth_client.get_access_token()
            self._token = StoredToken(
                access_token=access_token,
                expires_at=time.time() + expires_in,
            )
            return self._token.access_token

    def clear_token(self) -> None:
        self._token = None

    def _is_expired(self, token: StoredToken) -> bool:
        return time.time() >= token.expires_at - _EXPIRY_BUFFER_SECONDS
