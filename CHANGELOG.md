# Changelog

All notable changes to the Tax990 Python SDK are documented here.

## [0.1.0] — Initial release

### Added
- `Tax990Client` entry point with `form990n`, `organizations`, `filing_status`, `webhooks`, `api_keys` resources
- Two-step OAuth flow: local HS256 JWS signing → RS256 access token via `GET /Auth/GetTax990Token`
- `TokenManager` with automatic caching and refresh (30 s pre-expiry buffer, asyncio.Lock deduplication)
- `Form990NResource`: `submit`, `create`, `update`, `get`, `list`, `delete`, `validate`, `transmit`, `get_pdf`, `status`
- `OrganizationResource`: `list`, `get`
- `FilingStatusResource`: `get`
- `WebhookResource` and `ApiKeysResource` stubs (not documented in Tax990 Public API)
- `HttpClient` (httpx) with exponential-backoff retry on 5xx/429/network errors (3 retries)
- Pydantic v2 models for all request/response shapes
- `validate_ein` and `format_ein` utilities (pattern from ANALYSIS.md)
- `verify_webhook_signature` HMAC-SHA256 utility
- Full async/await API (Python 3.9+)
- `production` and `sandbox` environment presets
- pytest + pytest-asyncio + respx test suite
- Four runnable examples
