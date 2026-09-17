import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from tax990 import Tax990Client
from tax990.models.form990n import CreatePayload, TransmitPayload, UpdatePayload

load_dotenv()

client = Tax990Client(
    client_id=os.environ.get("TAX990_CLIENT_ID", ""),
    client_secret=os.environ.get("TAX990_CLIENT_SECRET", ""),
    user_token=os.environ.get("TAX990_USER_TOKEN", ""),
    api_url=os.environ.get("TAX990_API_URL") or None,
    oauth_url=os.environ.get("TAX990_OAUTH_URL") or None,
)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def fail(exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"StatusCode": 500, "StatusMessage": str(exc)})


def csv(value: Optional[str]) -> Optional[list[str]]:
    return value.split(",") if value else None


# ─── Auth ────────────────────────────────────────────────────────
@app.post("/api/auth/token")
async def auth_token():
    try:
        result = await client.utility.ping()
        return {"StatusCode": 200, "Message": "Authenticated", "PingResult": result}
    except Exception as exc:
        return fail(exc)


@app.get("/api/auth/server-time")
async def server_time():
    try:
        return await client.utility.ping()
    except Exception as exc:
        return fail(exc)


# ─── Form 990-N ──────────────────────────────────────────────────
@app.post("/api/form990n/create")
async def form990n_create(request: Request, idempotency_key: Optional[str] = Header(None)):
    try:
        payload = CreatePayload.model_validate(await request.json())
        return await client.form990n.create(payload, idempotency_key)
    except Exception as exc:
        return fail(exc)


@app.post("/api/form990n/update")
async def form990n_update(request: Request):
    try:
        payload = UpdatePayload.model_validate(await request.json())
        return await client.form990n.update(payload)
    except Exception as exc:
        return fail(exc)


@app.get("/api/form990n/get")
async def form990n_get(
    submission_id: str = Query(alias="SubmissionId"),
    record_id: Optional[str] = Query(None, alias="RecordId"),
):
    try:
        return await client.form990n.get(submission_id, record_id)
    except Exception as exc:
        return fail(exc)


@app.get("/api/form990n/list")
async def form990n_list(
    submission_id: Optional[str] = Query(None, alias="SubmissionId"),
    business_id: Optional[str] = Query(None, alias="BusinessId"),
):
    try:
        return await client.form990n.list(submission_id, business_id)
    except Exception as exc:
        return fail(exc)


@app.delete("/api/form990n/delete")
async def form990n_delete(
    submission_id: str = Query(alias="SubmissionId"),
    record_id: Optional[str] = Query(None, alias="RecordId"),
):
    try:
        return await client.form990n.delete(submission_id, record_id)
    except Exception as exc:
        return fail(exc)


@app.get("/api/form990n/validate")
async def form990n_validate(
    submission_id: str = Query(alias="SubmissionId"),
    record_ids: str = Query(alias="RecordIds"),
):
    try:
        return await client.form990n.validate(submission_id, csv(record_ids) or [])
    except Exception as exc:
        return fail(exc)


@app.post("/api/form990n/transmit")
async def form990n_transmit(request: Request):
    try:
        payload = TransmitPayload.model_validate(await request.json())
        return await client.form990n.transmit(payload)
    except Exception as exc:
        return fail(exc)


@app.get("/api/form990n/getPDF")
async def form990n_get_pdf(
    submission_id: str = Query(alias="SubmissionId"),
    record_ids: Optional[str] = Query(None, alias="RecordIds"),
):
    try:
        return await client.form990n.get_pdf(submission_id, csv(record_ids))
    except Exception as exc:
        return fail(exc)


@app.get("/api/form990n/status")
async def form990n_status(
    submission_id: str = Query(alias="SubmissionId"),
    record_ids: Optional[str] = Query(None, alias="RecordIds"),
):
    try:
        return await client.form990n.status(submission_id, csv(record_ids))
    except Exception as exc:
        return fail(exc)


# ─── Utility ─────────────────────────────────────────────────────
@app.get("/api/utility/ping")
async def utility_ping():
    try:
        return await client.utility.ping()
    except Exception as exc:
        return fail(exc)


@app.get("/api/utility/getAllSubmissionId")
async def utility_all_submission_ids():
    try:
        return await client.utility.get_all_submission_id()
    except Exception as exc:
        return fail(exc)


@app.get("/api/utility/getSubmissionIdByBusinessId")
async def utility_submission_id_by_business_id(businessId: str = Query()):
    try:
        return await client.utility.get_submission_id_by_business_id(businessId)
    except Exception as exc:
        return fail(exc)


@app.get("/api/utility/getSubmissionIdByRecordId")
async def utility_submission_id_by_record_id(recordId: str = Query()):
    try:
        return await client.utility.get_submission_id_by_record_id(recordId)
    except Exception as exc:
        return fail(exc)


@app.get("/api/utility/getRecordIds")
async def utility_record_ids():
    try:
        return await client.utility.get_record_ids()
    except Exception as exc:
        return fail(exc)


@app.get("/api/utility/getRecordIdBySubmissionId")
async def utility_record_id_by_submission_id(submissionId: str = Query()):
    try:
        return await client.utility.get_record_id_by_submission_id(submissionId)
    except Exception as exc:
        return fail(exc)


@app.get("/api/utility/getRecordDetailBySubmissionId")
async def utility_record_detail_by_submission_id(submissionId: str = Query()):
    try:
        return await client.utility.get_record_detail_by_submission_id(submissionId)
    except Exception as exc:
        return fail(exc)


@app.get("/api/utility/getAllBusinessId")
async def utility_all_business_ids():
    try:
        return await client.utility.get_all_business_id()
    except Exception as exc:
        return fail(exc)


@app.get("/api/utility/getBusinessIdBySubmissionId")
async def utility_business_id_by_submission_id(submissionId: str = Query()):
    try:
        return await client.utility.get_business_id_by_submission_id(submissionId)
    except Exception as exc:
        return fail(exc)


# ─── Nonprofits ──────────────────────────────────────────────────
@app.get("/api/nonprofits/getOrganizationDetailsByEIN")
async def nonprofits_get_by_ein(ein: str = Query()):
    try:
        return await client.nonprofits.get_organization_details_by_ein(ein)
    except Exception as exc:
        return fail(exc)
