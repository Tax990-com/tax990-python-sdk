from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import httpx
import jwt as pyjwt
import pytest
import respx

from tax990.auth.oauth_client import OAuthClient
from tax990.auth.token_manager import TokenManager
from tax990.errors.exceptions import AuthError
from tax990.http.http_client import HttpClient
from tests.fixtures.auth_fixtures import (
    TOKEN_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALID_CONFIG,
)

OAUTH_BASE = "http://localhost:4000"


def make_oauth_client() -> OAuthClient:
    http = HttpClient(base_url=OAUTH_BASE)
    return OAuthClient(
        http=http,
        client_id=VALID_CONFIG["client_id"],
        client_secret=VALID_CONFIG["client_secret"],
        user_token=VALID_CONFIG["user_token"],
    )


# ---------------------------------------------------------------------------
# OAuthClient
# ---------------------------------------------------------------------------


def test_sign_jws_locally_produces_valid_hs256() -> None:
    oauth = make_oauth_client()
    jws = oauth.sign_jws_locally()

    decoded = pyjwt.decode(
        jws,
        VALID_CONFIG["client_secret"],
        algorithms=["HS256"],
        audience=VALID_CONFIG["user_token"],
    )

    assert decoded["iss"] == VALID_CONFIG["client_id"]
    assert decoded["sub"] == VALID_CONFIG["client_id"]
    assert decoded["aud"] == VALID_CONFIG["user_token"]
    assert "iat" in decoded


@respx.mock
async def test_get_access_token_success() -> None:
    respx.get(f"{OAUTH_BASE}/Auth/GetTax990Token").mock(
        return_value=httpx.Response(200, json=TOKEN_RESPONSE)
    )
    oauth = make_oauth_client()
    access_token, expires_in = await oauth.get_access_token()

    assert access_token == TOKEN_RESPONSE["response"]["AccessToken"]
    assert expires_in == 3600


@respx.mock
async def test_get_access_token_raises_auth_error_on_body_errors() -> None:
    respx.get(f"{OAUTH_BASE}/Auth/GetTax990Token").mock(
        return_value=httpx.Response(200, json=UNAUTHORIZED_RESPONSE)
    )
    oauth = make_oauth_client()
    with pytest.raises(AuthError):
        await oauth.get_access_token()


@respx.mock
async def test_get_access_token_raises_auth_error_on_http_401() -> None:
    respx.get(f"{OAUTH_BASE}/Auth/GetTax990Token").mock(
        return_value=httpx.Response(401, json={"StatusMessage": "Unauthorized"})
    )
    oauth = make_oauth_client()
    with pytest.raises(AuthError):
        await oauth.get_access_token()


# ---------------------------------------------------------------------------
# TokenManager
# ---------------------------------------------------------------------------


async def test_token_manager_returns_and_caches_token() -> None:
    mock_oauth = MagicMock()
    mock_oauth.get_access_token = AsyncMock(return_value=("test-token", 3600))

    manager = TokenManager(oauth_client=mock_oauth)

    token1 = await manager.get_token()
    token2 = await manager.get_token()

    assert token1 == "test-token"
    assert token2 == "test-token"
    assert mock_oauth.get_access_token.call_count == 1


async def test_token_manager_refreshes_after_clear() -> None:
    mock_oauth = MagicMock()
    mock_oauth.get_access_token = AsyncMock(
        side_effect=[("token-1", 3600), ("token-2", 3600)]
    )

    manager = TokenManager(oauth_client=mock_oauth)

    t1 = await manager.get_token()
    manager.clear_token()
    t2 = await manager.get_token()

    assert t1 == "token-1"
    assert t2 == "token-2"
    assert mock_oauth.get_access_token.call_count == 2


async def test_token_manager_deduplicates_concurrent_refreshes() -> None:
    event = asyncio.Event()
    call_count = 0

    async def slow_get_access_token() -> tuple[str, int]:
        nonlocal call_count
        call_count += 1
        await event.wait()
        return "concurrent-token", 3600

    mock_oauth = MagicMock()
    mock_oauth.get_access_token = slow_get_access_token

    manager = TokenManager(oauth_client=mock_oauth)

    tasks = [asyncio.create_task(manager.get_token()) for _ in range(3)]
    await asyncio.sleep(0)
    event.set()
    results = await asyncio.gather(*tasks)

    assert all(r == "concurrent-token" for r in results)
    assert call_count == 1
