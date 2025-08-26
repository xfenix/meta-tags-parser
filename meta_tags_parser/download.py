import httpx


def download_page_sync(uri_of_page: str) -> str:
    """Download page synchronously."""
    response_obj = httpx.get(uri_of_page)
    return response_obj.text


async def download_page_async(uri_of_page: str) -> str:
    """Download page asynchronously."""
    async with httpx.AsyncClient() as client:
        request_obj = await client.get(uri_of_page)
        return request_obj.text
