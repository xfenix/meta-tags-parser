from unittest.mock import AsyncMock

import pytest
from faker import Faker

from meta_tags_parser import download


@pytest.mark.asyncio
async def test_async_download(monkeypatch: pytest.MonkeyPatch, faker: Faker) -> None:
    monkeypatch.setattr("httpx.AsyncClient", AsyncMock)
    await download.download_page_async(faker.url())
