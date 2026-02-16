from __future__ import annotations

import asyncio

from metaway_api.infra.database import AsyncSessionLocal
from metaway_api.infra.seed import seed_initial_data


async def _run() -> None:
    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
