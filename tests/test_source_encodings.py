"""Pages arrive as raw bytes in whatever encoding the site served, parsing must survive all of them."""

import typing

import hypothesis
import hypothesis.strategies as st
import pytest

from meta_tags_parser import parse_meta_tags_from_source, parse_snippets_from_source, structs


RUSSIAN_SAMPLE_TEXT: typing.Final = "Привет, мир"
JAPANESE_SAMPLE_TEXT: typing.Final = "日本語のページ"


def _build_page_source(sample_text: str, charset_declaration: str = "") -> str:
    return (
        f"<html><head>{charset_declaration}<title>{sample_text}</title>"
        f'<meta property="og:title" content="{sample_text}"></head></html>'
    )


@pytest.mark.parametrize(
    ("declared_charset", "used_encoding", "sample_text"),
    [
        ("windows-1251", "windows-1251", RUSSIAN_SAMPLE_TEXT),
        ("cp1251", "windows-1251", RUSSIAN_SAMPLE_TEXT),
        ("Shift_JIS", "shift_jis", JAPANESE_SAMPLE_TEXT),
        ("utf-8", "utf-8", RUSSIAN_SAMPLE_TEXT),
        ("UTF-8", "utf-8", JAPANESE_SAMPLE_TEXT),
    ],
)
def test_declared_charset_is_honoured(declared_charset: str, used_encoding: str, sample_text: str) -> None:
    page_bytes: typing.Final[bytes] = _build_page_source(sample_text, f'<meta charset="{declared_charset}">').encode(
        used_encoding
    )

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_bytes)

    assert parse_result.title == sample_text
    assert parse_result.open_graph == [structs.OneMetaTag(name="title", value=sample_text)]


def test_http_equiv_charset_declaration_is_honoured() -> None:
    page_bytes: typing.Final[bytes] = _build_page_source(
        RUSSIAN_SAMPLE_TEXT, '<meta http-equiv="Content-Type" content="text/html; charset=windows-1251">'
    ).encode("windows-1251")

    assert parse_meta_tags_from_source(page_bytes).title == RUSSIAN_SAMPLE_TEXT


@pytest.mark.parametrize("bom_encoding", ["utf-8-sig", "utf-16", "utf-32"])
def test_byte_order_mark_wins_over_the_default_encoding(bom_encoding: str) -> None:
    page_bytes: typing.Final[bytes] = _build_page_source(JAPANESE_SAMPLE_TEXT).encode(bom_encoding)

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_bytes)

    assert parse_result.title == JAPANESE_SAMPLE_TEXT
    assert parse_snippets_from_source(page_bytes).open_graph.title == JAPANESE_SAMPLE_TEXT


def test_missing_declaration_falls_back_to_utf8() -> None:
    assert parse_meta_tags_from_source(_build_page_source(RUSSIAN_SAMPLE_TEXT).encode()).title == RUSSIAN_SAMPLE_TEXT


@pytest.mark.parametrize("declared_charset", ["base64", "hex", "rot13", "zip", "uu", "idna", "totally-unknown-9000"])
def test_charset_that_cannot_decode_text_does_not_break_parsing(declared_charset: str) -> None:
    """Pages declare all kinds of nonsense, an unknown name or a non text codec must not hide the markup."""
    page_bytes: typing.Final[bytes] = _build_page_source(
        JAPANESE_SAMPLE_TEXT, f'<meta charset="{declared_charset}">'
    ).encode()

    assert parse_meta_tags_from_source(page_bytes).title == JAPANESE_SAMPLE_TEXT


@pytest.mark.parametrize("declared_charset", ["punycode", "utf-16", "utf-32"])
def test_charset_that_mangles_the_page_still_returns_a_result(declared_charset: str) -> None:
    """A codec that decodes into garbage cannot be detected, parsing still has to come back with a group."""
    page_bytes: typing.Final[bytes] = _build_page_source(
        JAPANESE_SAMPLE_TEXT, f'<meta charset="{declared_charset}">'
    ).encode()

    assert isinstance(parse_meta_tags_from_source(page_bytes), structs.TagsGroup)


def test_undecodable_bytes_are_dropped_instead_of_raising() -> None:
    assert parse_meta_tags_from_source(b'<meta charset="utf-8"><title>\xff\xfe broken').title == "broken"


@hypothesis.given(page_bytes=st.binary(max_size=200))
def test_arbitrary_bytes_are_parsed_without_errors(page_bytes: bytes) -> None:
    assert isinstance(parse_meta_tags_from_source(page_bytes), structs.TagsGroup)
    assert isinstance(parse_snippets_from_source(page_bytes), structs.SnippetGroup)
