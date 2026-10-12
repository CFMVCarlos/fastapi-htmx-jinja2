import asyncio
import time
from typing import Any, cast

from app.routers.extensions import ConnectionManager


class MockWebSocket:
    async def send_text(self, text: str) -> None:
        pass


async def main() -> None:
    manager = ConnectionManager()
    # Add many connections
    for _ in range(10000):
        manager.active_connections.append(cast(Any, MockWebSocket()))

    time.perf_counter()
    for _ in range(100):
        await manager.send_message("Test message")
    time.perf_counter()


if __name__ == "__main__":
    asyncio.run(main())
