"""Concurrent HTTPX stock checks with timeout, retries, and bounded parallelism."""
import asyncio
import httpx

async def fetch_product(client: httpx.AsyncClient, base_url: str, product_id: int, semaphore: asyncio.Semaphore, *, attempts: int = 3):
    async with semaphore:
        for attempt in range(attempts):
            try:
                response = await client.get(f"{base_url.rstrip('/')}/products/{product_id}")
                response.raise_for_status()
                return response.json()
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as exc:
                retryable = not isinstance(exc, httpx.HTTPStatusError) or exc.response.status_code in (429, 500, 502, 503, 504)
                if attempt == attempts - 1 or not retryable:
                    raise
                await asyncio.sleep(min(0.1 * 2**attempt, 1.0))

async def fetch_many_products(base_url: str, product_ids: list[int], *, max_concurrent: int = 3, timeout: float = 5.0, attempts: int = 3, client: httpx.AsyncClient | None = None):
    semaphore = asyncio.Semaphore(max_concurrent)
    async def run(active_client):
        tasks = [asyncio.create_task(fetch_product(active_client, base_url, pid, semaphore, attempts=attempts)) for pid in product_ids]
        try:
            return await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout * max(1, len(product_ids)))
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
    if client is not None:
        return await run(client)
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as active_client:
        return await run(active_client)
