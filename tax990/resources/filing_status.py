from __future__ import annotations

from typing import List, Optional, Union

from tax990.http.http_client import HttpClient
from tax990.models.common import ApiResponse
from tax990.models.form990n import ErrorRecord, SuccessRecord


class FilingStatusResource:
    """Wraps GET /v1/form990n/status."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get(
        self,
        submission_id: str,
        record_ids: Optional[Union[str, List[str]]] = None,
    ) -> ApiResponse[SuccessRecord, ErrorRecord]:
        ids: Optional[str] = None
        if isinstance(record_ids, list):
            ids = ",".join(record_ids)
        elif record_ids:
            ids = record_ids
        data = await self._http.get(
            "/v1/form990n/status",
            params={"SubmissionId": submission_id, "RecordIds": ids},
        )
        return ApiResponse[SuccessRecord, ErrorRecord].model_validate(data)
