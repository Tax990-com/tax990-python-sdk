from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

S = TypeVar("S")
E = TypeVar("E")


class StructuredError(BaseModel):
    Classification: str
    Code: str
    Message: str
    Field: Optional[str] = None


class Form990NRecordsContainer(BaseModel, Generic[S, E]):
    SuccessRecords: Optional[List[S]] = None
    ErrorRecords: Optional[List[E]] = None


class ApiResponse(BaseModel, Generic[S, E]):
    StatusCode: int
    StatusNm: str
    StatusMessage: str
    CorrelationId: str
    SubmissionId: Optional[str] = None
    Form990NRecords: Optional[Form990NRecordsContainer[S, E]] = None
    Errors: Optional[List[StructuredError]] = None


class Pagination(BaseModel):
    """Pagination is not implemented in the Tax990 Public API (ANALYSIS.md §Pagination: None)."""

    pass
