from __future__ import annotations

from typing import Any

from tax990.http.http_client import HttpClient


class NonprofitsResource:
    """Wraps the /v1/nonprofits/* endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get_organization_details_by_ein(self, ein: str) -> Any:
        """GET /v1/nonprofits/getOrganizationDetailsByEIN"""
        data = await self._http.get(
            "/v1/nonprofits/getOrganizationDetailsByEIN",
            params={"ein": ein},
        )
        return data
