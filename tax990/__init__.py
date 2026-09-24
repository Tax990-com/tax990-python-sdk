from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from tax990.auth.oauth_client import OAuthClient
from tax990.auth.token_manager import TokenManager
from tax990.errors.exceptions import (  # noqa: F401
    AuthError,
    NotFoundError,
    RateLimitError,
    Tax990Error,
    ValidationError,
)
from tax990.http.http_client import HttpClient
from tax990.models.common import ApiResponse, Pagination, StructuredError  # noqa: F401
from tax990.models.form990n import (  # noqa: F401
    Business,
    CreatePayload,
    ErrorRecord,
    ForeignAddress,
    Form990NData,
    Form990NRecord,
    GetSuccessRecord,
    PDFRecord,
    PDFResponse,
    PrincipalOfficer,
    SuccessRecord,
    TransmitErrorRecord,
    TransmitPayload,
    TransmitSuccessRecord,
    UpdatePayload,
    USAddress,
    ValidateErrorRecord,
    ValidateSuccessRecord,
    ValidationWarning,
)
from tax990.resources.api_keys import ApiKeysResource
from tax990.resources.filing_status import FilingStatusResource
from tax990.resources.form990n import Form990NResource
from tax990.resources.nonprofits import NonprofitsResource
from tax990.resources.organization import OrganizationResource
from tax990.resources.utility import UtilityResource
from tax990.utils.ein_validator import format_ein, validate_ein  # noqa: F401
from tax990.utils.webhook_verifier import verify_webhook_signature  # noqa: F401


class Tax990Client:
    """
    Main entry point for the Tax990 Python SDK.

    Usage::

        import asyncio
        from tax990 import Tax990Client

        client = Tax990Client(
            client_id="...",
            client_secret="...",
            user_token="...",
            environment="production",
        )

        result = await client.form990n.submit(payload)
    """

    form990n: Form990NResource
    organizations: OrganizationResource
    filing_status: FilingStatusResource
    utility: UtilityResource
    nonprofits: NonprofitsResource
    api_keys: ApiKeysResource

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_token: str,
        environment: str = "sandbox",
        api_url: Optional[str] = None,
        oauth_url: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        _api_url = api_url or os.environ.get("TAX990_API_URL", "")
        _oauth_url = oauth_url or os.environ.get("TAX990_OAUTH_URL", "")

        oauth_http = HttpClient(base_url=_oauth_url, timeout=timeout)
        oauth_client = OAuthClient(
            http=oauth_http,
            client_id=client_id,
            client_secret=client_secret,
            user_token=user_token,
        )
        token_manager = TokenManager(oauth_client=oauth_client)

        api_http = HttpClient(
            base_url=_api_url,
            timeout=timeout,
            get_token=token_manager.get_token,
        )

        self.form990n = Form990NResource(http=api_http)
        self.organizations = OrganizationResource(http=api_http)
        self.filing_status = FilingStatusResource(http=api_http)
        self.utility = UtilityResource(http=api_http)
        self.nonprofits = NonprofitsResource(http=api_http)
        self.api_keys = ApiKeysResource()
