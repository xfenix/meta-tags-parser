import unittest.mock

import pytest
from faker import Faker

from meta_tags_parser import download


@pytest.mark.asyncio
async def test_async_download(monkeypatch: pytest.MonkeyPatch, faker: Faker) -> None:
    monkeypatch.setattr("httpx.AsyncClient", unittest.mock.AsyncMock)
    await download.download_page_async(faker.url())
