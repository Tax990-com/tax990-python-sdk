from __future__ import annotations

import asyncio
import uuid
from typing import Any, Awaitable, Callable, Optional

import httpx

from tax990.errors.exceptions import (
    AuthError,
    NotFoundError,
    RateLimitError,
    Tax990Error,
    ValidationError,
)
from tax990.models.common import StructuredError

_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 0.5


class HttpClient:
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        get_token: Optional[Callable[[], Awaitable[str]]] = None,
    ) -> None:
        self._get_token = get_token
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    async def get(
        self,
        path: str,
        params: Optional[dict[str, Optional[str]]] = None,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> Any:
        headers = await self._build_headers(extra_headers)
        clean_params = _clean_params(params)
        response = await self._request_with_retry(
            "GET", path, params=clean_params, headers=headers
        )
        return _parse_response(response)

    async def post(
        self,
        path: str,
        json: Optional[Any] = None,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> Any:
        headers = await self._build_headers(extra_headers)
        response = await self._request_with_retry(
            "POST", path, json=json, headers=headers
        )
        return _parse_response(response)

    async def delete(
        self,
        path: str,
        params: Optional[dict[str, Optional[str]]] = None,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> Any:
        headers = await self._build_headers(extra_headers)
        clean_params = _clean_params(params)
        response = await self._request_with_retry(
            "DELETE", path, params=clean_params, headers=headers
        )
        return _parse_response(response)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _build_headers(
        self, extra: Optional[dict[str, str]] = None
    ) -> dict[str, str]:
        headers: dict[str, str] = {"x-correlation-id": str(uuid.uuid4())}
        if extra:
            headers.update(extra)
        if self._get_token:
            token = await self._get_token()
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def _request_with_retry(
        self, method: str, path: str, **kwargs: Any
    ) -> httpx.Response:
        for attempt in range(_MAX_RETRIES + 1):
            try:
                response = await self._client.request(method, path, **kwargs)
                should_retry = (
                    response.status_code in _RETRY_STATUS_CODES
                    and attempt < _MAX_RETRIES
                )
                if should_retry:
                    await asyncio.sleep(_RETRY_BASE_DELAY * (2**attempt))
                    continue
                return response
            except httpx.RequestError as exc:
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(_RETRY_BASE_DELAY * (2**attempt))
                    continue
                raise Tax990Error(str(exc), "NETWORK_ERROR", 0) from exc
        raise RuntimeError("Max retries exceeded")  # unreachable


def _parse_response(response: httpx.Response) -> Any:
    if response.is_success:
        return response.json()
    _raise_for_response(response)


def _raise_for_response(response: httpx.Response) -> None:
    try:
        data: dict[str, Any] = response.json()
    except Exception:
        data = {}

    correlation_id: Optional[str] = data.get("CorrelationId")
    status_code = response.status_code
    message: str = (
        data.get("StatusMessage")
        or data.get("message")
        or response.text
        or "Unknown error"
    )

    if status_code == 401:
        raise AuthError(message, correlation_id)
    if status_code == 404:
        raise NotFoundError(message, correlation_id)
    if status_code == 429:
        raise RateLimitError(message, correlation_id)
    if status_code == 400:
        raw_errors = data.get("Errors") or []
        if raw_errors:
            errors = [StructuredError.model_validate(e) for e in raw_errors]
            raise ValidationError(message, errors, correlation_id)

    raise Tax990Error(message, str(status_code), status_code, correlation_id)


def _clean_params(
    params: Optional[dict[str, Optional[str]]],
) -> dict[str, str]:
    if not params:
        return {}
    return {k: v for k, v in params.items() if v is not None}
