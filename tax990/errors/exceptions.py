from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from tax990.models.common import StructuredError


class Tax990Error(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        correlation_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.correlation_id = correlation_id


class AuthError(Tax990Error):
    def __init__(self, message: str, correlation_id: Optional[str] = None) -> None:
        super().__init__(message, "AUTH_ERROR", 401, correlation_id)


class ValidationError(Tax990Error):
    def __init__(
        self,
        message: str,
        errors: "List[StructuredError]",
        correlation_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, "VALIDATION_ERROR", 400, correlation_id)
        self.errors = errors


class RateLimitError(Tax990Error):
    def __init__(self, message: str, correlation_id: Optional[str] = None) -> None:
        super().__init__(message, "RATE_LIMIT_ERROR", 429, correlation_id)


class NotFoundError(Tax990Error):
    def __init__(self, message: str, correlation_id: Optional[str] = None) -> None:
        super().__init__(message, "NOT_FOUND", 404, correlation_id)
