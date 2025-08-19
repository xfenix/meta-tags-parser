from __future__ import annotations

import pytest

from meta_tags_parser import public


def test_public_download(monkeypatch: pytest.MonkeyPatch, provide_fake_meta: tuple[dict[str, str], str]) -> None:
    """Test download via public API."""

    # pylint: disable=too-few-public-methods
    class FakeHttpXObject:
        """Provide duck-typing mock."""

        @property
        def text(self) -> str:
            """Return fake text.

            Hello, duck-type
            """
            return provide_fake_meta[1]

    monkeypatch.setattr("httpx.get", lambda _: FakeHttpXObject())
    public.parse_tags_from_url("https://yandex.ru")
    public.parse_snippets_from_url("https://yandex.ru")


@pytest.mark.asyncio
async def test_async_public_download(
    monkeypatch: pytest.MonkeyPatch, provide_fake_meta: tuple[dict[str, str], str]
) -> None:
    """Test async download via public API."""

    async def _fake_download(_: str) -> str:
        return provide_fake_meta[1]

    monkeypatch.setattr("meta_tags_parser.download.download_page_async", _fake_download)
    await public.parse_tags_from_url_async("https://yandex.ru")
    await public.parse_snippets_from_url_async("https://yandex.ru")
