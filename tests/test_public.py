"""There."""
from meta_tags_parser import public

import pytest


def test_public_download():
    public.parse_tags_from_url("https://yandex.ru")


@pytest.mark.asyncio
async def test_public_download():
    await public.parse_tags_from_url_async("https://yandex.ru")


__all__ = ["test_public_download"]
