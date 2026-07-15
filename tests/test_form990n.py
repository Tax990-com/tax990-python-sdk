from __future__ import annotations

import httpx
import pytest
import respx

from tax990.errors.exceptions import ValidationError
from tax990.http.http_client import HttpClient
from tax990.resources.form990n import Form990NResource
from tax990.utils.ein_validator import format_ein, validate_ein
from tests.fixtures.form990n_fixtures import (
    CREATE_PAYLOAD,
    CREATE_RESPONSE,
    TRANSMIT_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)

API_BASE = "http://localhost:9005"


def make_resource() -> Form990NResource:
    return Form990NResource(http=HttpClient(base_url=API_BASE))


# ---------------------------------------------------------------------------
# create / submit
# ---------------------------------------------------------------------------


@respx.mock
async def test_create_posts_to_correct_endpoint() -> None:
    route = respx.post(f"{API_BASE}/v1/form990n/create").mock(
        return_value=httpx.Response(200, json=CREATE_RESPONSE)
    )
    resource = make_resource()
    result = await resource.create(CREATE_PAYLOAD)

    assert route.called
    assert result.StatusCode == 200
    assert result.Form990NRecords is not None
    assert result.Form990NRecords.SuccessRecords is not None
    assert result.Form990NRecords.SuccessRecords[0].RecordStatus == "Created"


@respx.mock
async def test_submit_is_alias_for_create() -> None:
    respx.post(f"{API_BASE}/v1/form990n/create").mock(
        return_value=httpx.Response(200, json=CREATE_RESPONSE)
    )
    resource = make_resource()
    result = await resource.submit(CREATE_PAYLOAD)

    assert result.StatusCode == 200


@respx.mock
async def test_create_sends_idempotency_key_header() -> None:
    route = respx.post(f"{API_BASE}/v1/form990n/create").mock(
        return_value=httpx.Response(200, json=CREATE_RESPONSE)
    )
    resource = make_resource()
    await resource.create(CREATE_PAYLOAD, idempotency_key="my-key-123")

    assert route.calls.last.request.headers.get("idempotency-key") == "my-key-123"


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


@respx.mock
async def test_get_passes_submission_id_as_query_param() -> None:
    route = respx.get(f"{API_BASE}/v1/form990n/get").mock(
        return_value=httpx.Response(200, json=CREATE_RESPONSE)
    )
    resource = make_resource()
    await resource.get(submission_id="sub-123")

    assert route.called
    assert "SubmissionId=sub-123" in str(route.calls.last.request.url)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


@respx.mock
async def test_list_passes_submission_id() -> None:
    route = respx.get(f"{API_BASE}/v1/form990n/list").mock(
        return_value=httpx.Response(200, json=CREATE_RESPONSE)
    )
    resource = make_resource()
    await resource.list(submission_id="sub-123")

    assert route.called
    assert "SubmissionId=sub-123" in str(route.calls.last.request.url)


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


@respx.mock
async def test_delete_uses_delete_method() -> None:
    route = respx.delete(f"{API_BASE}/v1/form990n/delete").mock(
        return_value=httpx.Response(200, json=CREATE_RESPONSE)
    )
    resource = make_resource()
    await resource.delete(submission_id="sub-123")

    assert route.called


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


@respx.mock
async def test_validate_joins_list_record_ids_with_comma() -> None:
    route = respx.get(f"{API_BASE}/v1/form990n/validate").mock(
        return_value=httpx.Response(200, json=CREATE_RESPONSE)
    )
    resource = make_resource()
    await resource.validate(submission_id="sub-123", record_ids=["r1", "r2", "r3"])

    assert route.called
    assert "RecordIds=r1%2Cr2%2Cr3" in str(route.calls.last.request.url) or "RecordIds=r1,r2,r3" in str(route.calls.last.request.url)


# ---------------------------------------------------------------------------
# transmit
# ---------------------------------------------------------------------------


@respx.mock
async def test_transmit_posts_to_correct_endpoint() -> None:
    from tax990.models.form990n import TransmitPayload

    route = respx.post(f"{API_BASE}/v1/form990n/transmit").mock(
        return_value=httpx.Response(200, json=TRANSMIT_RESPONSE)
    )
    resource = make_resource()
    result = await resource.transmit(TransmitPayload(SubmissionId="sub-123"))

    assert route.called
    assert result.StatusCode == 200


# ---------------------------------------------------------------------------
# error mapping
# ---------------------------------------------------------------------------


@respx.mock
async def test_create_raises_validation_error_on_400() -> None:
    respx.post(f"{API_BASE}/v1/form990n/create").mock(
        return_value=httpx.Response(400, json=VALIDATION_ERROR_RESPONSE)
    )
    resource = make_resource()
    with pytest.raises(ValidationError) as exc_info:
        await resource.create(CREATE_PAYLOAD)

    assert exc_info.value.status_code == 400
    assert len(exc_info.value.errors) == 1
    assert exc_info.value.errors[0].Code == "F990N001"


# ---------------------------------------------------------------------------
# EIN validator
# ---------------------------------------------------------------------------


def test_validate_ein_accepts_nine_digits() -> None:
    assert validate_ein("123456789") is True


def test_validate_ein_accepts_formatted() -> None:
    assert validate_ein("12-3456789") is True


def test_validate_ein_rejects_short() -> None:
    assert validate_ein("1234") is False


def test_validate_ein_rejects_letters() -> None:
    assert validate_ein("abc123456") is False


def test_format_ein_adds_hyphen() -> None:
    assert format_ein("123456789") == "12-3456789"


def test_format_ein_idempotent_on_formatted() -> None:
    assert format_ein("12-3456789") == "12-3456789"


def test_format_ein_raises_on_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid EIN"):
        format_ein("123")
