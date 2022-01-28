"""Simple public interface tests."""
import pytest

from meta_tags_parser import public


def test_public_download(monkeypatch, provide_fake_meta):
    """Public download test in integration manere."""

    # pylint: disable=too-few-public-methods
    class FakeHttpXObject:
        """Duck-typing mock."""

        @property
        def text(self):
            """Just faky fake.

            Hello, duck-type
            """
            return provide_fake_meta[1]

    monkeypatch.setattr("httpx.get", lambda _: FakeHttpXObject())
    public.parse_tags_from_url("https://yandex.ru")
    public.parse_snippets_from_url("https://yandex.ru")


@pytest.mark.asyncio
async def test_async_public_download(monkeypatch, provide_fake_meta):
    """Async download in unit style."""

    async def _fake_download(_):
        return provide_fake_meta[1]

    monkeypatch.setattr("meta_tags_parser.download.download_page_async", _fake_download)
    await public.parse_tags_from_url_async("https://yandex.ru")
    await public.parse_snippets_from_url_async("https://yandex.ru")
