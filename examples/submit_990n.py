"""
Submit a Form 990-N filing.

Run:
    python examples/submit_990n.py
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

from tax990 import Tax990Client
from tax990.errors.exceptions import AuthError, Tax990Error, ValidationError
from tax990.models.form990n import (
    Business,
    CreatePayload,
    Form990NData,
    Form990NRecord,
    PrincipalOfficer,
    USAddress,
)

load_dotenv()


async def main() -> None:
    client = Tax990Client(
        client_id=os.environ["TAX990_CLIENT_ID"],
        client_secret=os.environ["TAX990_CLIENT_SECRET"],
        user_token=os.environ["TAX990_USER_TOKEN"],
        environment=os.environ.get("TAX990_ENVIRONMENT", "sandbox"),
    )

    payload = CreatePayload(
        Form990NRecords=[
            Form990NRecord(
                Business=Business(
                    BusinessId=None,
                    BusinessNm="Example Nonprofit Org",
                    EIN="12-3456789",
                    DBANm=None,
                    InCareOfNm=None,
                    EmailAddress="contact@example.org",
                    Phone="5125550100",
                    IsForeign=False,
                    USAddress=USAddress(
                        Address1="100 Main St",
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
                    WebsiteAddress=None,
                    PrincipalOfficer=PrincipalOfficer(
                        OfficerNm="Jane Smith",
                        IsForeign=False,
                        USAddress=USAddress(
                            Address1="100 Main St",
                            Address2=None,
                            City="Austin",
                            State="TX",
                            ZipCd="78701",
                        ),
                        ForeignAddress=None,
                    ),
                ),
            )
        ]
    )

    try:
        result = await client.form990n.submit(payload)
        print(f"Submission ID : {result.SubmissionId}")
        print(f"Status        : {result.StatusCode} {result.StatusNm}")
        records = result.Form990NRecords
        if records and records.SuccessRecords:
            for rec in records.SuccessRecords:
                print(f"  Record {rec.RecordId}: {rec.RecordStatus}")
        if records and records.ErrorRecords:
            for err in records.ErrorRecords:
                print(f"  Error record {err.RecordId}: {err.Errors}")
    except ValidationError as exc:
        print(f"Validation error: {exc}")
        for e in exc.errors:
            print(f"  [{e.Code}] {e.Field}: {e.Message}")
    except AuthError as exc:
        print(f"Authentication failed: {exc}")
    except Tax990Error as exc:
        print(f"API error ({exc.status_code}): {exc}")


if __name__ == "__main__":
    asyncio.run(main())
