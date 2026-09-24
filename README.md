# tax990-python-sdk

Official async Python SDK for the Tax990 Public API — IRS Form 990-N e-filing, utility lookups,
and nonprofit organization search.

🔗 API Reference: [developer.tax990.com](https://developer.tax990.com)

## Installation

```bash
pip install tax990-sdk
```

Or install from source:

```bash
pip install -e .
```

## Quick start

```python
import asyncio
import os
from tax990 import Tax990Client

async def main():
    client = Tax990Client(
        client_id=os.environ["TAX990_CLIENT_ID"],
        client_secret=os.environ["TAX990_CLIENT_SECRET"],
        user_token=os.environ["TAX990_USER_TOKEN"],
    )
    ping = await client.utility.ping()
    print(ping)

asyncio.run(main())
```

## Environment variables

Create a `.env` file in the repo root:

```
TAX990_CLIENT_ID=...
TAX990_CLIENT_SECRET=...
TAX990_USER_TOKEN=...
TAX990_API_URL=https://api-sandbox.tax990.com
TAX990_OAUTH_URL=https://oauth-sandbox.tax990.com
```

| Variable | Required | Description |
|---|---|---|
| `TAX990_CLIENT_ID` | ✅ | OAuth client identifier |
| `TAX990_CLIENT_SECRET` | ✅ | OAuth client secret, used to sign the JWS |
| `TAX990_USER_TOKEN` | ✅ | OAuth audience token for this client |
| `TAX990_API_URL` | ✅ | API base URL — production: `https://api.tax990.com`, sandbox: `https://api-sandbox.tax990.com` |
| `TAX990_OAUTH_URL` | ✅ | OAuth base URL — production: `https://oauth.tax990.com`, sandbox: `https://oauth-sandbox.tax990.com` |

`api_url=` / `oauth_url=` can be passed to `Tax990Client(...)` to override env vars at the call site.

## Available modules

### Form 990-N (`client.form990n`)

| Method | Endpoint | Description |
|---|---|---|
| `create(payload, idempotency_key?)` | `POST /v1/form990n/create` | Create a new filing |
| `update(payload)` | `POST /v1/form990n/update` | Update an existing filing |
| `get(submission_id, record_id?)` | `GET /v1/form990n/get` | Retrieve a filing by SubmissionId |
| `list(submission_id?, business_id?)` | `GET /v1/form990n/list` | List filings |
| `delete(submission_id, record_id?)` | `DELETE /v1/form990n/delete` | Delete an untransmitted filing |
| `validate(submission_id, record_ids)` | `GET /v1/form990n/validate` | Validate before transmit |
| `transmit(payload)` | `POST /v1/form990n/transmit` | E-file to the IRS |
| `get_pdf(submission_id, record_ids?)` | `GET /v1/form990n/getPDF` | Download PDF copies |
| `status(submission_id, record_ids?)` | `GET /v1/form990n/status` | Check IRS acknowledgement status |

### Utility (`client.utility`)

| Method | Endpoint | Description |
|---|---|---|
| `ping()` | `GET /v1/utility/ping` | Health check |
| `get_all_submission_id()` | `GET /v1/utility/getAllSubmissionId` | All submission IDs |
| `get_submission_id_by_business_id(business_id)` | `GET /v1/utility/getSubmissionIdByBusinessId` | Submission by business ID |
| `get_submission_id_by_record_id(record_id)` | `GET /v1/utility/getSubmissionIdByRecordId` | Submission by record ID |
| `get_record_ids()` | `GET /v1/utility/getRecordIds` | All record IDs |
| `get_record_id_by_submission_id(submission_id)` | `GET /v1/utility/getRecordIdBySubmissionId` | Records for a submission |
| `get_record_detail_by_submission_id(submission_id)` | `GET /v1/utility/getRecordDetailBySubmissionId` | Record details |
| `get_all_business_id()` | `GET /v1/utility/getAllBusinessId` | All business IDs |
| `get_business_id_by_submission_id(submission_id)` | `GET /v1/utility/getBusinessIdBySubmissionId` | Business ID for a submission |

### Nonprofits (`client.nonprofits`)

| Method | Endpoint | Description |
|---|---|---|
| `get_organization_details_by_ein(ein)` | `GET /v1/nonprofits/getOrganizationDetailsByEIN` | Nonprofit details by EIN |

Also available: `client.organizations`, `client.filing_status`.

## Typical workflow

1. `Tax990Client(...)` — instantiate
2. `await client.form990n.create(payload)` → store the returned `SubmissionId`
3. `await client.form990n.validate(...)` — catch errors before transmit (optional)
4. `await client.form990n.get_pdf(...)` — review the draft PDF (optional)
5. `await client.form990n.transmit(...)` — e-file to the IRS
6. `await client.form990n.status(...)` — poll for IRS acknowledgement

## Error handling

```python
from tax990.errors.exceptions import Tax990Error, AuthError, ValidationError

try:
    result = await client.form990n.create(payload)
except ValidationError as exc:
    for error in exc.errors:
        print(f"[{error.Code}] {error.Field}: {error.Message}")
except AuthError as exc:
    print(f"Auth failed: {exc}")
except Tax990Error as exc:
    print(f"API error ({exc.status_code}): {exc}")
```

## Utilities

```python
from tax990 import validate_ein, format_ein, verify_webhook_signature

validate_ein("12-3456789")  # True
format_ein("123456789")     # "12-3456789"
```

## Running tests

```bash
pip install -e ".[dev]"
pytest
```

## Bridge server (for use with tax990-ui-sdk)

`bridge.py` is a FastAPI app that exposes all SDK methods as REST endpoints, so the
`tax990-ui-sdk` React app can exercise this SDK through its UI.

```bash
pip install -e ".[dev]"

# start bridge on http://localhost:4100
uvicorn bridge:app --port 4100 --reload
```

Then in `tax990-ui-sdk`, set `VITE_BRIDGE_URL=http://localhost:4100` and run `npm run dev`.

## Project structure

```
tax990-python-sdk/
├── tax990/
│   ├── auth/          oauth_client.py, token_manager.py
│   ├── errors/        exceptions.py — Tax990Error and subclasses
│   ├── http/          http_client.py (httpx wrapper, bearer injection)
│   ├── models/        Pydantic models
│   ├── resources/     form990n.py, utility.py, nonprofits.py, ...
│   ├── utils/         ein_validator.py, webhook_verifier.py
│   └── __init__.py    Tax990Client — package entry point
├── bridge.py          FastAPI bridge server for tax990-ui-sdk
├── examples/
├── tests/
└── pyproject.toml
```

## Tech stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.9+, `asyncio` |
| HTTP | `httpx` |
| Models | `pydantic` v2 |
| Auth | OAuth 2.0, JWS (HS256) via `pyjwt` |
| Bridge | FastAPI + uvicorn |
| Tests | `pytest`, `pytest-asyncio`, `respx` |

## License
