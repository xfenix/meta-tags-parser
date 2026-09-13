import dataclasses
import typing

import httpx
import pytest

from meta_tags_parser import download, public, structs
from tests import conftest


REDIRECT_TARGET_URL: typing.Final = "https://example.com/final-page"
STARTING_URL: typing.Final = "https://example.com/start"


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class RecordedRequest:
    """Captures how the library called httpx, without touching the network."""

    keyword_arguments: dict[str, typing.Any] = dataclasses.field(default_factory=dict)


def _build_mock_transport(page_source: str) -> httpx.MockTransport:
    def _handle_request(one_request: httpx.Request) -> httpx.Response:
        if str(one_request.url) == STARTING_URL:
            return httpx.Response(status_code=301, headers={"location": REDIRECT_TARGET_URL})
        return httpx.Response(status_code=200, text=page_source)

    return httpx.MockTransport(_handle_request)


@pytest.fixture(name="recorded_request")
def provide_recorded_request(
    monkeypatch: pytest.MonkeyPatch, provide_fake_meta_page: conftest.FakeMetaPage
) -> RecordedRequest:
    """Replace httpx entry points with mock transport backed ones and remember the call arguments."""
    recorded_request: typing.Final = RecordedRequest()
    mock_transport: typing.Final[httpx.MockTransport] = _build_mock_transport(provide_fake_meta_page.html_source)
    original_async_client: typing.Final = httpx.AsyncClient

    def _handle_sync_get(request_url: str, **keyword_arguments: typing.Any) -> httpx.Response:  # noqa: ANN401
        recorded_request.keyword_arguments.clear()
        recorded_request.keyword_arguments.update(keyword_arguments)
        with httpx.Client(transport=mock_transport, **keyword_arguments) as sync_client:
            return sync_client.get(request_url)

    def _make_async_client(**keyword_arguments: typing.Any) -> httpx.AsyncClient:  # noqa: ANN401
        recorded_request.keyword_arguments.clear()
        recorded_request.keyword_arguments.update(keyword_arguments)
        return original_async_client(transport=mock_transport, **keyword_arguments)

    monkeypatch.setattr("httpx.get", _handle_sync_get)
    monkeypatch.setattr("httpx.AsyncClient", _make_async_client)
    return recorded_request


def test_sync_download_follows_redirects_and_sets_a_timeout(recorded_request: RecordedRequest) -> None:
    page_source: typing.Final[str] = download.download_page_sync(STARTING_URL)

    assert recorded_request.keyword_arguments["follow_redirects"] is True
    assert recorded_request.keyword_arguments["timeout"] == download.DEFAULT_REQUEST_TIMEOUT
    assert "user-agent" in recorded_request.keyword_arguments["headers"]
    assert "og:title" in page_source


@pytest.mark.asyncio
async def test_async_download_follows_redirects_and_sets_a_timeout(recorded_request: RecordedRequest) -> None:
    page_source: typing.Final[str] = await download.download_page_async(STARTING_URL)

    assert recorded_request.keyword_arguments["follow_redirects"] is True
    assert recorded_request.keyword_arguments["timeout"] == download.DEFAULT_REQUEST_TIMEOUT
    assert "og:title" in page_source


def test_custom_timeout_is_passed_through(recorded_request: RecordedRequest) -> None:
    download.download_page_sync(STARTING_URL, request_timeout=1.5)

    assert recorded_request.keyword_arguments["timeout"] == 1.5


@pytest.mark.usefixtures("recorded_request")
def test_parse_tags_from_url(provide_fake_meta_page: conftest.FakeMetaPage) -> None:
    parse_result: typing.Final[structs.TagsGroup] = public.parse_tags_from_url(STARTING_URL)

    assert parse_result.title
    assert parse_result.open_graph
    assert {one_meta_tag.name for one_meta_tag in parse_result.open_graph} <= set(
        provide_fake_meta_page.social_tag_values
    )


@pytest.mark.usefixtures("recorded_request")
def test_parse_snippets_from_url() -> None:
    snippet_result: typing.Final[structs.SnippetGroup] = public.parse_snippets_from_url(STARTING_URL)

    assert snippet_result.open_graph.title
    assert snippet_result.twitter.title


@pytest.mark.usefixtures("recorded_request")
def test_options_reach_the_parser_through_the_url_helpers() -> None:
    parse_result: typing.Final[structs.TagsGroup] = public.parse_tags_from_url(
        STARTING_URL, options=structs.SettingsFromUser(what_to_parse=(structs.WhatToParse.TITLE,))
    )

    assert parse_result.title
    assert parse_result.open_graph == []


@pytest.mark.asyncio
@pytest.mark.usefixtures("recorded_request")
async def test_async_url_helpers() -> None:
    parse_result: typing.Final[structs.TagsGroup] = await public.parse_tags_from_url_async(STARTING_URL)
    snippet_result: typing.Final[structs.SnippetGroup] = await public.parse_snippets_from_url_async(STARTING_URL)

    assert parse_result.open_graph
    assert snippet_result.twitter.title
