import types
import typing

import httpx


DEFAULT_REQUEST_TIMEOUT: typing.Final = 10.0
DEFAULT_REQUEST_HEADERS: typing.Final[typing.Mapping[str, str]] = types.MappingProxyType(
    {"user-agent": "meta-tags-parser (+https://github.com/xfenix/meta-tags-parser)"}
)


def download_page_sync(uri_of_page: str, *, request_timeout: float = DEFAULT_REQUEST_TIMEOUT) -> str:
    return httpx.get(
        uri_of_page,
        timeout=request_timeout,
        follow_redirects=True,
        headers=dict(DEFAULT_REQUEST_HEADERS),
    ).text


async def download_page_async(uri_of_page: str, *, request_timeout: float = DEFAULT_REQUEST_TIMEOUT) -> str:
    async with httpx.AsyncClient(
        timeout=request_timeout,
        follow_redirects=True,
        headers=dict(DEFAULT_REQUEST_HEADERS),
    ) as client:
        return (await client.get(uri_of_page)).text
