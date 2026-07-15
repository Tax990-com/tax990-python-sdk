from __future__ import annotations

import uuid
from typing import List, Optional, Union

from tax990.http.http_client import HttpClient
from tax990.models.common import ApiResponse
from tax990.models.form990n import (
    CreatePayload,
    ErrorRecord,
    GetSuccessRecord,
    PDFResponse,
    SuccessRecord,
    TransmitErrorRecord,
    TransmitPayload,
    TransmitSuccessRecord,
    UpdatePayload,
    ValidateErrorRecord,
    ValidateSuccessRecord,
)


class Form990NResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        payload: CreatePayload,
        idempotency_key: Optional[str] = None,
    ) -> ApiResponse[SuccessRecord, ErrorRecord]:
        key = idempotency_key or str(uuid.uuid4())
        data = await self._http.post(
            "/v1/form990n/create",
            json=payload.model_dump(mode="json"),
            extra_headers={"idempotency-key": key},
        )
        return ApiResponse[SuccessRecord, ErrorRecord].model_validate(data)

    async def submit(
        self,
        payload: CreatePayload,
        idempotency_key: Optional[str] = None,
    ) -> ApiResponse[SuccessRecord, ErrorRecord]:
        return await self.create(payload, idempotency_key)

    async def update(
        self,
        payload: UpdatePayload,
    ) -> ApiResponse[SuccessRecord, ErrorRecord]:
        data = await self._http.post(
            "/v1/form990n/update",
            json=payload.model_dump(mode="json"),
        )
        return ApiResponse[SuccessRecord, ErrorRecord].model_validate(data)

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

    async def delete(
        self,
        submission_id: str,
        record_id: Optional[str] = None,
    ) -> ApiResponse[SuccessRecord, ErrorRecord]:
        data = await self._http.delete(
            "/v1/form990n/delete",
            params={"SubmissionId": submission_id, "RecordId": record_id},
        )
        return ApiResponse[SuccessRecord, ErrorRecord].model_validate(data)

    async def validate(
        self,
        submission_id: str,
        record_ids: Union[str, List[str]],
    ) -> ApiResponse[ValidateSuccessRecord, ValidateErrorRecord]:
        ids = ",".join(record_ids) if isinstance(record_ids, list) else record_ids
        data = await self._http.get(
            "/v1/form990n/validate",
            params={"SubmissionId": submission_id, "RecordIds": ids},
        )
        return ApiResponse[ValidateSuccessRecord, ValidateErrorRecord].model_validate(data)

    async def transmit(
        self,
        payload: TransmitPayload,
    ) -> ApiResponse[TransmitSuccessRecord, TransmitErrorRecord]:
        data = await self._http.post(
            "/v1/form990n/transmit",
            json=payload.model_dump(mode="json"),
        )
        return ApiResponse[TransmitSuccessRecord, TransmitErrorRecord].model_validate(data)

    async def get_pdf(
        self,
        submission_id: str,
        record_ids: Optional[Union[str, List[str]]] = None,
    ) -> PDFResponse:
        ids: Optional[str] = None
        if isinstance(record_ids, list):
            ids = ",".join(record_ids)
        elif record_ids:
            ids = record_ids
        data = await self._http.get(
            "/v1/form990n/getPDF",
            params={"SubmissionId": submission_id, "RecordIds": ids},
        )
        return PDFResponse.model_validate(data)

    async def status(
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
