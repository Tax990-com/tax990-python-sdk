# tax990-sdk — Python

Official Python SDK for the Tax990 Public API.

## Installation

```bash
pip install tax990-sdk
```

Or for local development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
import os
from tax990 import Tax990Client
from tax990.models.form990n import (
    Business, CreatePayload, Form990NData, Form990NRecord,
    PrincipalOfficer, USAddress,
)

client = Tax990Client(
    client_id=os.environ["TAX990_CLIENT_ID"],
    client_secret=os.environ["TAX990_CLIENT_SECRET"],
    user_token=os.environ["TAX990_USER_TOKEN"],
    environment="production",  # or "sandbox"
)

payload = CreatePayload(
    Form990NRecords=[
        Form990NRecord(
            Business=Business(
                BusinessNm="Example Nonprofit",
                EIN="12-3456789",
                IsForeign=False,
                USAddress=USAddress(
                    Address1="100 Main St", City="Austin", State="TX", ZipCd="78701"
                ),
            ),
            Form990N=Form990NData(
                SequenceId="1",
                TaxYr="2024",
                TaxPeriodBeginDt="2024-01-01",
                TaxPeriodEndDt="2024-12-31",
                IsGrossReceiptsUnder50K=True,
                IsOrganizationTerminated=False,
                PrincipalOfficer=PrincipalOfficer(
                    OfficerNm="Jane Smith",
                    IsForeign=False,
                    USAddress=USAddress(
                        Address1="100 Main St", City="Austin", State="TX", ZipCd="78701"
                    ),
                ),
            ),
        )
    ]
)

async def main():
    result = await client.form990n.submit(payload)
    print("SubmissionId:", result.SubmissionId)

asyncio.run(main())
```

## Configuration

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `client_id` | `str` | Yes | — | Your Client ID |
| `client_secret` | `str` | Yes | — | Your Client Secret |
| `user_token` | `str` | Yes | — | Your User Token |
| `environment` | `str` | No | `"sandbox"` | `"production"` or `"sandbox"` |
| `api_url` | `str` | No | env default | Override Form990N API base URL |
| `oauth_url` | `str` | No | env default | Override OAuth API base URL |
| `timeout` | `int` | No | `30` | Request timeout in seconds |

**Environment URLs:**

| Environment | API URL | OAuth URL |
|-------------|---------|-----------|
| `production` | `https://api.tax990.com` | `https://oauth.tax990.com` |
| `sandbox` | `http://localhost:9005` | `http://localhost:4000` |

## Authentication

Authentication follows the two-step Tax990 OAuth flow (see ANALYSIS.md §1):

1. A JWS is signed locally using **HS256** with `client_secret`
   - Claims: `iss`=client_id, `sub`=client_id, `aud`=user_token, `iat`=now
2. The JWS is sent to `GET /Auth/GetTax990Token` via `authentication` header
3. The server returns an **RS256** access token (expires in 3600 s)

`TokenManager` handles caching and auto-renewal transparently (refreshes 30 s before expiry).

## API Reference

### `client.form990n`

All methods are `async`.

| Method | HTTP | Endpoint | Description |
|--------|------|----------|-------------|
| `submit(payload, idempotency_key?)` | POST | `/v1/form990n/create` | Alias for `create` |
| `create(payload, idempotency_key?)` | POST | `/v1/form990n/create` | Create filing records |
| `update(payload)` | POST | `/v1/form990n/update` | Update existing records |
| `get(submission_id, record_id?)` | GET | `/v1/form990n/get` | Fetch a record |
| `list(submission_id?, business_id?)` | GET | `/v1/form990n/list` | List records |
| `delete(submission_id, record_id?)` | DELETE | `/v1/form990n/delete` | Delete records |
| `validate(submission_id, record_ids)` | GET | `/v1/form990n/validate` | Validate records |
| `transmit(payload)` | POST | `/v1/form990n/transmit` | Transmit to IRS |
| `get_pdf(submission_id, record_ids?)` | GET | `/v1/form990n/getPDF` | Get PDF URLs |
| `status(submission_id, record_ids?)` | GET | `/v1/form990n/status` | Get filing status |

### `client.organizations`

| Method | Description |
|--------|-------------|
| `list(submission_id?, business_id?)` | List org records via `form990n/list` |
| `get(submission_id, record_id?)` | Get org record via `form990n/get` |

### `client.filing_status`

| Method | Description |
|--------|-------------|
| `get(submission_id, record_ids?)` | Get filing status via `form990n/status` |

### `client.webhooks` and `client.api_keys`

These resources are not documented in the Tax990 Public API and raise `NotImplementedError`.

## Error Handling

```python
from tax990.errors.exceptions import (
    AuthError, ValidationError, NotFoundError, RateLimitError, Tax990Error
)

try:
    result = await client.form990n.submit(payload)
except ValidationError as exc:
    for e in exc.errors:
        print(f"[{e.Code}] {e.Field}: {e.Message}")
except AuthError as exc:
    print("Auth failed:", exc)
except NotFoundError as exc:
    print("Not found:", exc)
except RateLimitError:
    print("Rate limited — retry later")
except Tax990Error as exc:
    print(f"API error {exc.status_code}: {exc}")
```

## Utilities

```python
from tax990.utils.ein_validator import validate_ein, format_ein
from tax990.utils.webhook_verifier import verify_webhook_signature
from tax990.models.webhook import WebhookVerifyOptions

validate_ein("12-3456789")   # True
validate_ein("123456789")    # True
format_ein("123456789")      # "12-3456789"

ok = verify_webhook_signature(
    WebhookVerifyOptions(secret="...", payload="...", signature="...")
)
```

## Development

```bash
pip install -e ".[dev]"

pytest                # run tests
mypy tax990/          # type check
ruff check .          # lint
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```
TAX990_CLIENT_ID=your_client_id
TAX990_CLIENT_SECRET=your_client_secret_id
TAX990_USER_TOKEN=your_user_token
TAX990_ENVIRONMENT=sandbox
```
