import typing

import httpx


def download_page_sync(uri_of_page: str) -> str:
    response_obj: typing.Final[httpx.Response] = httpx.get(uri_of_page)
    return response_obj.text


async def download_page_async(uri_of_page: str) -> str:
    async with httpx.AsyncClient() as client:
        response_obj: typing.Final[httpx.Response] = await client.get(uri_of_page)
        return response_obj.text
