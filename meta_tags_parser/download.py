"""Downloader functions."""
import httpx


def download_page_sync(uri_of_page: str) -> str:
    """Simple yet stupid downloader."""
    return httpx.get(uri_of_page).text


async def download_page_async(uri_of_page: str) -> str:
    """Simple yet stupid async downloader."""
    async with httpx.AsyncClient() as client:
        request_obj: httpx.Response = await client.get(uri_of_page)
        return request_obj.text


__all__ = ["download_page_async", "download_page_sync"]
