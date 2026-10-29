import asyncio
from unittest.mock import AsyncMock


async def fetch_reorder_status(provider, code: str):
    return await provider.fetch_status(code)


def test_async_reorder_provider():
    provider = AsyncMock()
    provider.fetch_status.return_value = {"code": "SKU-1", "status": "ordered"}
    result = asyncio.run(fetch_reorder_status(provider, "SKU-1"))
    assert result["status"] == "ordered"
    provider.fetch_status.assert_awaited_once_with("SKU-1")
