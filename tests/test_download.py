"""There."""
from unittest.mock import AsyncMock

from meta_tags_parser import download

import pytest


@pytest.mark.asyncio
async def test_async_download(monkeypatch, faker):
    monkeypatch.setattr("httpx.AsyncClient", AsyncMock)
    await download.download_page_async(faker.url())


__all__ = [
    'test_async_download'
]
