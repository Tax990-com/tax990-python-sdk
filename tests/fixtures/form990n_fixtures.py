from __future__ import annotations

from typing import Any

from tax990.models.form990n import (
    Business,
    CreatePayload,
    Form990NData,
    Form990NRecord,
    PrincipalOfficer,
    USAddress,
)

US_RECORD = Form990NRecord(
    Business=Business(
        BusinessId=None,
        BusinessNm="Test Nonprofit Org",
        EIN="12-3456789",
        DBANm=None,
        InCareOfNm=None,
        EmailAddress="test@example.org",
        Phone="5551234567",
        IsForeign=False,
        USAddress=USAddress(
            Address1="123 Main St",
            Address2=None,
            City="Austin",
            State="TX",
            ZipCd="78701",
        ),
        ForeignAddress=None,
    ),
    Form990N=Form990NData(
        SequenceId="1",
        RecordId=None,
        TaxYr="2024",
        TaxPeriodBeginDt="2024-01-01",
        TaxPeriodEndDt="2024-12-31",
        IsGrossReceiptsUnder50K=True,
        IsOrganizationTerminated=False,
        WebsiteAddress="https://example.org",
        PrincipalOfficer=PrincipalOfficer(
            OfficerNm="Jane Smith",
            IsForeign=False,
            USAddress=USAddress(
                Address1="123 Main St",
                Address2=None,
                City="Austin",
                State="TX",
                ZipCd="78701",
            ),
            ForeignAddress=None,
        ),
    ),
)

CREATE_PAYLOAD = CreatePayload(Form990NRecords=[US_RECORD])

CREATE_RESPONSE: dict[str, Any] = {
    "StatusCode": 200,
    "StatusNm": "Ok",
    "StatusMessage": "Successful API call",
    "CorrelationId": "correlation-id-123",
    "SubmissionId": "submission-uuid-456",
    "Form990NRecords": {
        "SuccessRecords": [
            {
                "SequenceId": "1",
                "RecordId": "record-uuid-789",
                "BusinessId": "business-uuid-101",
                "RecordStatus": "Created",
                "CreatedTs": "2024-01-15T10:00:00.000Z",
                "UpdatedTs": "2024-01-15T10:00:00.000Z",
            }
        ],
        "ErrorRecords": None,
    },
    "Errors": None,
}

TRANSMIT_RESPONSE: dict[str, Any] = {
    "StatusCode": 200,
    "StatusNm": "Ok",
    "StatusMessage": "Transmitted",
    "CorrelationId": "correlation-id-789",
    "SubmissionId": "submission-uuid-456",
    "Form990NRecords": {
        "SuccessRecords": [
            {
                "SequenceId": "1",
                "RecordId": "record-uuid-789",
                "Status": "Transmitted",
                "StatusTs": None,
            }
        ],
        "ErrorRecords": None,
    },
    "Errors": None,
}

VALIDATION_ERROR_RESPONSE: dict[str, Any] = {
    "StatusCode": 400,
    "StatusNm": "BadRequest",
    "StatusMessage": "A validation error has occurred.",
    "CorrelationId": "correlation-id-456",
    "SubmissionId": None,
    "Form990NRecords": None,
    "Errors": [
        {
            "Classification": "validation",
            "Code": "F990N001",
            "Message": "EIN is invalid",
            "Field": "EIN",
        }
    ],
}
