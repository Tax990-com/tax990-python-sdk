import asyncio
import os
import sys

from tax990 import Tax990Client


async def main():
    client = Tax990Client(
        client_id=os.environ["TAX990_CLIENT_ID"],
        client_secret=os.environ["TAX990_CLIENT_SECRET"],
        user_token=os.environ["TAX990_USER_TOKEN"],
        environment="sandbox",
    )

    ein = sys.argv[1] if len(sys.argv) > 1 else "123456789"
    result = await client.nonprofits.get_organization_details_by_ein(ein=ein)
    print(f"Organization: {result}")


if __name__ == "__main__":
    asyncio.run(main())
