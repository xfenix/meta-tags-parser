"""Test simple download helpers (stupid tests of course)."""
from __future__ import annotations
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from meta_tags_parser import download


if TYPE_CHECKING:
    from faker import Faker


@pytest.mark.asyncio
async def test_async_download(monkeypatch: pytest.MonkeyPatch, faker: Faker) -> None:
    """Run async download helper."""
    monkeypatch.setattr("httpx.AsyncClient", AsyncMock)
    await download.download_page_async(faker.url())
