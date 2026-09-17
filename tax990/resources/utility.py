from __future__ import annotations

from typing import Any, Optional

from tax990.http.http_client import HttpClient


class UtilityResource:
    """Wraps the /v1/utility/* endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def ping(self) -> Any:
        """GET /v1/utility/ping — no authentication required."""
        data = await self._http.get("/v1/utility/ping")
        return data

    async def get_all_submission_id(self) -> Any:
        """GET /v1/utility/getAllSubmissionId"""
        data = await self._http.get("/v1/utility/getAllSubmissionId")
        return data

    async def get_submission_id_by_business_id(self, business_id: str) -> Any:
        """GET /v1/utility/getSubmissionIdByBusinessId"""
        data = await self._http.get(
            "/v1/utility/getSubmissionIdByBusinessId",
            params={"businessId": business_id},
        )
        return data

    async def get_submission_id_by_record_id(self, record_id: str) -> Any:
        """GET /v1/utility/getSubmissionIdByRecordId"""
        data = await self._http.get(
            "/v1/utility/getSubmissionIdByRecordId",
            params={"recordId": record_id},
        )
        return data

    async def get_record_ids(self) -> Any:
        """GET /v1/utility/getRecordIds"""
        data = await self._http.get("/v1/utility/getRecordIds")
        return data

    async def get_record_id_by_submission_id(self, submission_id: str) -> Any:
        """GET /v1/utility/getRecordIdBySubmissionId"""
        data = await self._http.get(
            "/v1/utility/getRecordIdBySubmissionId",
            params={"submissionId": submission_id},
        )
        return data

    async def get_record_detail_by_submission_id(self, submission_id: str) -> Any:
        """GET /v1/utility/getRecordDetailBySubmissionId"""
        data = await self._http.get(
            "/v1/utility/getRecordDetailBySubmissionId",
            params={"submissionId": submission_id},
        )
        return data

    async def get_all_business_id(self) -> Any:
        """GET /v1/utility/getAllBusinessId"""
        data = await self._http.get("/v1/utility/getAllBusinessId")
        return data

    async def get_business_id_by_submission_id(self, submission_id: str) -> Any:
        """GET /v1/utility/getBusinessIdBySubmissionId"""
        data = await self._http.get(
            "/v1/utility/getBusinessIdBySubmissionId",
            params={"submissionId": submission_id},
        )
        return data
