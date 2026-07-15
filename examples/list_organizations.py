"""
List organizations (businesses) associated with a submission.

Run:
    TAX990_SUBMISSION_ID=<id> python examples/list_organizations.py
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

    submission_id = os.environ.get("TAX990_SUBMISSION_ID")
    business_id = os.environ.get("TAX990_BUSINESS_ID")

    if not submission_id and not business_id:
        print("Set TAX990_SUBMISSION_ID or TAX990_BUSINESS_ID to list organizations.")
        return

    try:
        result = await client.organizations.list(
            submission_id=submission_id,
            business_id=business_id,
        )
        print(f"Status: {result.StatusCode} {result.StatusNm}")
        records = result.Form990NRecords
        if records and records.SuccessRecords:
            print(f"Found {len(records.SuccessRecords)} record(s):")
            for rec in records.SuccessRecords:
                biz = rec.Business
                name = biz.BusinessNm if biz else "Unknown"
                ein = biz.EIN if biz else "N/A"
                print(f"  {rec.RecordId}: {name} (EIN: {ein}) — {rec.RecordStatus}")
        else:
            print("No records found.")
    except NotFoundError:
        print("No organizations found for the given parameters.")
    except Tax990Error as exc:
        print(f"API error ({exc.status_code}): {exc}")


if __name__ == "__main__":
    asyncio.run(main())
