from typing import List, Optional

from pydantic import BaseModel

from tax990.models.common import StructuredError


class USAddress(BaseModel):
    Address1: Optional[str] = None
    Address2: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    ZipCd: Optional[str] = None


class ForeignAddress(BaseModel):
    Address1: Optional[str] = None
    Address2: Optional[str] = None
    City: Optional[str] = None
    ProvinceOrStateNm: Optional[str] = None
    Country: Optional[str] = None
    PostalCd: Optional[str] = None


# Python's bytecode executes the value assignment (= None) BEFORE storing the
# annotation, so `USAddress = None` would shadow the class `USAddress` inside
# `Optional[USAddress]`.  Proxy aliases sidestep this: the field is still named
# `USAddress` (matching the API JSON key) but the type annotation references the
# proxy `_USAddress`, which is never a field name and is never shadowed.
_USAddress = USAddress
_ForeignAddress = ForeignAddress


class Business(BaseModel):
    BusinessId: Optional[str] = None
    BusinessNm: Optional[str] = None
    EIN: Optional[str] = None
    DBANm: Optional[str] = None
    InCareOfNm: Optional[str] = None
    EmailAddress: Optional[str] = None
    Phone: Optional[str] = None
    IsForeign: Optional[bool] = None
    USAddress: Optional[_USAddress] = None
    ForeignAddress: Optional[_ForeignAddress] = None


class PrincipalOfficer(BaseModel):
    OfficerNm: Optional[str] = None
    IsForeign: Optional[bool] = None
    USAddress: Optional[_USAddress] = None
    ForeignAddress: Optional[_ForeignAddress] = None


_PrincipalOfficer = PrincipalOfficer


class Form990NData(BaseModel):
    SequenceId: Optional[str] = None
    RecordId: Optional[str] = None
    TaxYr: Optional[str] = None
    TaxPeriodBeginDt: Optional[str] = None
    TaxPeriodEndDt: Optional[str] = None
    IsGrossReceiptsUnder50K: Optional[bool] = None
    IsOrganizationTerminated: Optional[bool] = None
    WebsiteAddress: Optional[str] = None
    PrincipalOfficer: Optional[_PrincipalOfficer] = None


class Form990NRecord(BaseModel):
    # No default value — required fields. Python does not execute STORE_NAME for
    # annotation-only statements, so no shadowing occurs here.
    Business: Business
    Form990N: Form990NData


class CreatePayload(BaseModel):
    Form990NRecords: List[Form990NRecord]


class UpdatePayload(BaseModel):
    SubmissionId: str
    Form990NRecords: List[Form990NRecord]


class TransmitPayload(BaseModel):
    SubmissionId: str
    RecordIds: Optional[List[str]] = None


class SuccessRecord(BaseModel):
    SequenceId: str
    RecordId: str
    BusinessId: str
    RecordStatus: str
    CreatedTs: str
    UpdatedTs: str


class ErrorRecord(BaseModel):
    SequenceId: Optional[str] = None
    RecordId: Optional[str] = None
    BusinessId: Optional[str] = None
    RecordStatus: str = ""
    Errors: List[StructuredError] = []


class GetForm990NData(BaseModel):
    TaxYear: Optional[str] = None
    TaxPeriodBeginDate: Optional[str] = None
    TaxPeriodEndDate: Optional[str] = None
    IsGrossReceiptsUnder50K: Optional[bool] = None
    IsOrganizationTerminated: Optional[bool] = None
    WebsiteAddress: Optional[str] = None
    PrincipalOfficer: Optional[_PrincipalOfficer] = None


_Business = Business


class GetSuccessRecord(SuccessRecord):
    Business: Optional[_Business] = None
    Form990N: Optional[GetForm990NData] = None


class ValidationWarning(BaseModel):
    ErrorCode: str
    Name: str
    Message: str


class ValidateSuccessRecord(BaseModel):
    SequenceId: str
    RecordId: str
    Warnings: Optional[List[ValidationWarning]] = None


class ValidateErrorRecord(BaseModel):
    SequenceId: str
    RecordId: str
    Errors: List[ValidationWarning]


class TransmitSuccessRecord(BaseModel):
    SequenceId: str
    RecordId: str
    Status: str
    StatusTs: Optional[str] = None


class TransmitErrorRecord(BaseModel):
    SequenceId: str
    RecordId: str
    Status: str
    ErrorMessage: str


class PDFRecord(BaseModel):
    RecordId: str
    PDFUrl: str


class PDFErrorRecord(BaseModel):
    RecordId: str
    Message: str


class PDFResponse(BaseModel):
    StatusCode: int
    StatusName: str
    StatusMessage: str
    CorrelationId: str
    SubmissionId: str
    Form990NRecords: Optional[List[PDFRecord]] = None
    Errors: Optional[List[PDFErrorRecord]] = None
