import httpx


def download_page_sync(uri_of_page: str) -> str:
    return httpx.get(uri_of_page).text


async def download_page_async(uri_of_page: str) -> str:
    async with httpx.AsyncClient() as client:
        return (await client.get(uri_of_page)).text
