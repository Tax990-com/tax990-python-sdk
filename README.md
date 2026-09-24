# Tax990 Python SDK 2.0

## Overview

The Tax990 Python SDK 2.0.x is an async Python integration package for the Tax990 Public API. It
enables businesses and software providers to integrate IRS Form 990-N e-filing directly into their
applications, without hand-rolling OAuth, request signing, or response parsing.

This SDK provides:

- **`Tax990Client`** — a single entry point exposing typed resources for Form 990-N filing,
  utility ID lookups, and nonprofit organization lookups
- **Automatic OAuth 2.0 token management** — signs and refreshes access tokens transparently
  between calls
- **`async`/`await` throughout**, built on `httpx`
- **Pydantic models** for every request and response — validated, typed, IDE-friendly

A separate React UI ([`../frontend`](../frontend)) is included in this repository as a shared
playground for exercising any of the four language SDKs side by side. See
[`../UI_INTEGRATION.md`](../UI_INTEGRATION.md) for a full FastAPI bridge server built on this exact
SDK, and [`../TESTING.md`](../TESTING.md) for the test walkthrough.

🔗 Full API Reference: [developer.tax990.com](https://developer.tax990.com)

## Project Structure

```
python/
├── tax990/
│   ├── auth/                # oauth_client.py, token_manager.py
│   ├── errors/                # exceptions.py — Tax990Error and subclasses
│   ├── http/                   # http_client.py (httpx wrapper, bearer injection)
│   ├── models/                   # common.py, form990n.py, webhook.py — Pydantic models
│   ├── resources/                 # form990n.py, utility.py, nonprofits.py, organization.py, ...
│   ├── utils/                       # ein_validator.py, webhook_verifier.py
│   └── __init__.py                   # Tax990Client — package entry point
├── examples/
│   ├── submit_990n.py
│   ├── check_filing_status.py
│   ├── list_organizations.py
│   ├── lookup_nonprofit.py
│   ├── handle_webhook.py
│   └── verify_webhook.py
├── tests/
│   ├── test_auth.py
│   ├── test_form990n.py
│   ├── test_webhook.py
│   └── fixtures/
└── pyproject.toml
```

## Installation

```bash
pip install tax990-sdk
```

Or, to install from source inside this repository:

```bash
cd python
pip install -e .
```

## Quick Start

```python
import asyncio
import os
from tax990 import Tax990Client

async def main():
    client = Tax990Client(
        client_id=os.environ["TAX990_CLIENT_ID"],
        client_secret=os.environ["TAX990_CLIENT_SECRET"],
        user_token=os.environ["TAX990_USER_TOKEN"],
        # API and OAuth URLs are read from TAX990_API_URL / TAX990_OAUTH_URL env vars
    )

    ping = await client.utility.ping()
    print(ping)

asyncio.run(main())
```

## Available API Modules

### Authentication

Handled automatically. `Tax990Client` signs a JWS locally with `client_secret`, exchanges it for
an access token against the OAuth endpoint, and caches/refreshes it before expiry — no manual
token handling required.

### Form 990-N (`client.form990n`)

Create, validate, and transmit IRS Form 990-N e-Postcard filings.

| Method | Endpoint | Description |
|---|---|---|
| `create(payload, idempotency_key?)` | `POST /v1/form990n/create` | Create and save a new Form 990-N filing |
| `submit(payload, idempotency_key?)` | `POST /v1/form990n/create` | Alias for `create` |
| `update(payload)` | `POST /v1/form990n/update` | Update an existing filing |
| `get(submission_id, record_id?)` | `GET /v1/form990n/get` | Retrieve a saved filing by SubmissionId |
| `list(submission_id?, business_id?)` | `GET /v1/form990n/list` | Paginated list of filings |
| `delete(submission_id, record_id?)` | `DELETE /v1/form990n/delete` | Delete an untransmitted filing |
| `validate(submission_id, record_ids)` | `GET /v1/form990n/validate` | Validate records before transmit |
| `transmit(payload)` | `POST /v1/form990n/transmit` | E-file to the IRS |
| `get_pdf(submission_id, record_ids?)` | `GET /v1/form990n/getPDF` | Download filing PDF copies |
| `status(submission_id, record_ids?)` | `GET /v1/form990n/status` | Check IRS acknowledgement status |

**Key fields:** `TaxYr`, `TaxPeriodBeginDt`/`EndDt`, `IsGrossReceiptsUnder50K`,
`IsOrganizationTerminated`, `PrincipalOfficer`, `Business.USAddress`/`ForeignAddress`.

### Utility (`client.utility`)

Health checks and cross-reference ID lookups.

| Method | Endpoint | Description |
|---|---|---|
| `ping()` | `GET /v1/utility/ping` | Health check |
| `get_all_submission_id()` | `GET /v1/utility/getAllSubmissionId` | Get all submission IDs |
| `get_submission_id_by_business_id(business_id)` | `GET /v1/utility/getSubmissionIdByBusinessId` | Look up submission by business ID |
| `get_submission_id_by_record_id(record_id)` | `GET /v1/utility/getSubmissionIdByRecordId` | Look up submission by record ID |
| `get_record_ids()` | `GET /v1/utility/getRecordIds` | Get all record IDs |
| `get_record_id_by_submission_id(submission_id)` | `GET /v1/utility/getRecordIdBySubmissionId` | Get records for a submission |
| `get_record_detail_by_submission_id(submission_id)` | `GET /v1/utility/getRecordDetailBySubmissionId` | Get record details for a submission |
| `get_all_business_id()` | `GET /v1/utility/getAllBusinessId` | Get all business IDs |
| `get_business_id_by_submission_id(submission_id)` | `GET /v1/utility/getBusinessIdBySubmissionId` | Get business ID for a submission |

### Nonprofits (`client.nonprofits`)

| Method | Endpoint | Description |
|---|---|---|
| `get_organization_details_by_ein(ein)` | `GET /v1/nonprofits/getOrganizationDetailsByEIN` | Look up nonprofit organization details by EIN |

Also available: `client.organizations` (business-entity queries over the same Form 990-N data) and
`client.filing_status` (a status-only convenience wrapper).

## Environment Variables

Set these in `python/.env` (loaded automatically via `python-dotenv`) or export them in your shell.

| Variable | Required | Description |
|---|---|---|
| `TAX990_CLIENT_ID` | ✅ | OAuth client identifier |
| `TAX990_CLIENT_SECRET` | ✅ | OAuth client secret, used to sign the JWS |
| `TAX990_USER_TOKEN` | ✅ | OAuth audience token for this client |
| `TAX990_API_URL` | ✅ | Public API base URL — production: `https://api.tax990.com`, sandbox: `https://api-sandbox.tax990.com` |
| `TAX990_OAUTH_URL` | ✅ | OAuth base URL — production: `https://oauth.tax990.com`, sandbox: `https://oauth-sandbox.tax990.com` |

`api_url=` / `oauth_url=` can be passed to `Tax990Client(...)` to override the env vars at the
call site.

## Typical Workflow

1. **Instantiate** → `Tax990Client(client_id=..., client_secret=..., user_token=...)`
2. **Create a filing** → `await client.form990n.create(payload)` → store the returned `SubmissionId`
3. **Validate (optional)** → `await client.form990n.validate(...)` to catch errors before transmit
4. **Review a draft** → `await client.form990n.get_pdf(...)` for a pre-transmission preview
5. **Transmit** → `await client.form990n.transmit(...)` to e-file with the IRS
6. **Track status** → `await client.form990n.status(...)` for acknowledgement status
7. **Look up organizations** → `await client.nonprofits.get_organization_details_by_ein(ein=...)` as needed

## Error Handling

```python
from tax990.errors.exceptions import (
    Tax990Error,       # Base error
    AuthError,         # 401 - Authentication failed
    ValidationError,   # 400 - Validation errors
    RateLimitError,    # 429 - Rate limit exceeded
    NotFoundError,     # 404 - Resource not found
)

try:
    result = await client.form990n.submit(payload)
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

## Testing

```bash
cd python
pip install -e ".[dev]"
pytest
```

## Documentation

🔗 [Tax990 Public API Docs](https://developer.tax990.com)

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.9+, `asyncio` |
| HTTP | `httpx` |
| Models | `pydantic` v2 |
| Auth | OAuth 2.0 Bearer tokens, JWS (HS256) via `pyjwt` |
| Tests | `pytest`, `pytest-asyncio`, `respx` |

## License

MIT — internal SDK for Tax990 Public API integration.
