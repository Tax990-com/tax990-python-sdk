"""
Check the filing status of a submission.

Run:
    TAX990_SUBMISSION_ID=<id> python examples/check_filing_status.py
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

from tax990 import Tax990Client
from tax990.errors.exceptions import NotFoundError, Tax990Error

load_dotenv()


async def main() -> None:
    client = Tax990Client(
        client_id=os.environ["TAX990_CLIENT_ID"],
        client_secret=os.environ["TAX990_CLIENT_SECRET"],
        user_token=os.environ["TAX990_USER_TOKEN"],
        environment=os.environ.get("TAX990_ENVIRONMENT", "sandbox"),
    )

    submission_id = os.environ.get("TAX990_SUBMISSION_ID", "")
    if not submission_id:
        print("Set TAX990_SUBMISSION_ID to check a specific submission.")
        return

    try:
        result = await client.filing_status.get(submission_id=submission_id)
        print(f"Submission ID : {result.SubmissionId}")
        print(f"Status code   : {result.StatusCode} {result.StatusNm}")
        records = result.Form990NRecords
        if records and records.SuccessRecords:
            for rec in records.SuccessRecords:
                print(f"  Record {rec.RecordId}: {rec.RecordStatus} (updated {rec.UpdatedTs})")
        if records and records.ErrorRecords:
            for err in records.ErrorRecords:
                print(f"  Error record {err.RecordId}")
    except NotFoundError:
        print(f"Submission '{submission_id}' not found.")
    except Tax990Error as exc:
        print(f"API error ({exc.status_code}): {exc}")


if __name__ == "__main__":
    asyncio.run(main())
