"""Test simple download helpers (stupid tests of course)."""
from unittest.mock import AsyncMock

import pytest

from meta_tags_parser import download


@pytest.mark.asyncio
async def test_async_download(monkeypatch, faker):
    """Stupid test..."""
    monkeypatch.setattr("httpx.AsyncClient", AsyncMock)
    await download.download_page_async(faker.url())


__all__ = ["test_async_download"]
