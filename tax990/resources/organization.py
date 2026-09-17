from __future__ import annotations

from typing import Optional

from tax990.http.http_client import HttpClient
from tax990.models.common import ApiResponse
from tax990.models.form990n import ErrorRecord, GetSuccessRecord


class OrganizationResource:
    """
    Organization data is embedded in Form990N records.
    Wraps form990n endpoints and surfaces the Business fields.
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(
        self,
        submission_id: Optional[str] = None,
        business_id: Optional[str] = None,
    ) -> ApiResponse[GetSuccessRecord, ErrorRecord]:
        data = await self._http.get(
            "/v1/form990n/list",
            params={"SubmissionId": submission_id, "BusinessId": business_id},
        )
        return ApiResponse[GetSuccessRecord, ErrorRecord].model_validate(data)

    async def get(
        self,
        submission_id: str,
        record_id: Optional[str] = None,
    ) -> ApiResponse[GetSuccessRecord, ErrorRecord]:
        data = await self._http.get(
            "/v1/form990n/get",
            params={"SubmissionId": submission_id, "RecordId": record_id},
        )
        return ApiResponse[GetSuccessRecord, ErrorRecord].model_validate(data)
