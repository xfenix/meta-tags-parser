import typing

import hypothesis
import hypothesis.strategies as st
import pytest

from meta_tags_parser.parse import convert_source_to_text


RUSSIAN_SAMPLE_TEXT: typing.Final = "Привет, мир"
JAPANESE_SAMPLE_TEXT: typing.Final = "日本語のページ"


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
def test_convert_source_to_text_honours_declared_charset(
    declared_charset: str, used_encoding: str, sample_text: str
) -> None:
    raw_source: typing.Final[bytes] = (
        f'<html><head><meta charset="{declared_charset}"><title>{sample_text}</title></head>'.encode(used_encoding)
    )

    assert sample_text in convert_source_to_text(raw_source)


def test_convert_source_to_text_honours_http_equiv_declaration() -> None:
    raw_source: typing.Final[bytes] = (
        '<html><head><meta http-equiv="Content-Type" content="text/html; charset=windows-1251">'
        f"<title>{RUSSIAN_SAMPLE_TEXT}</title></head>"
    ).encode("windows-1251")

    assert RUSSIAN_SAMPLE_TEXT in convert_source_to_text(raw_source)


@pytest.mark.parametrize("bom_encoding", ["utf-8-sig", "utf-16", "utf-32"])
def test_convert_source_to_text_honours_byte_order_mark(bom_encoding: str) -> None:
    raw_source: typing.Final[bytes] = f"<title>{RUSSIAN_SAMPLE_TEXT}</title>".encode(bom_encoding)

    decoded_source: typing.Final[str] = convert_source_to_text(raw_source)

    assert decoded_source == f"<title>{RUSSIAN_SAMPLE_TEXT}</title>"


@pytest.mark.parametrize("declared_charset", ["base64", "hex", "rot13", "zip", "uu", "idna", "punycode"])
def test_convert_source_to_text_survives_non_text_charsets(declared_charset: str) -> None:
    """Pages declare all kinds of nonsense, a codec that cannot decode text must not crash parsing."""
    raw_source: typing.Final[bytes] = f'<meta charset="{declared_charset}"><title>plain</title>'.encode()

    assert isinstance(convert_source_to_text(raw_source), str)


def test_convert_source_to_text_ignores_unknown_charset() -> None:
    raw_source: typing.Final = b'<meta charset="totally-unknown-9000"><title>plain</title>'

    assert "plain" in convert_source_to_text(raw_source)


def test_convert_source_to_text_falls_back_to_utf8_without_declaration() -> None:
    assert convert_source_to_text(f"<title>{RUSSIAN_SAMPLE_TEXT}</title>".encode()) == (
        f"<title>{RUSSIAN_SAMPLE_TEXT}</title>"
    )


def test_convert_source_to_text_never_raises_on_broken_bytes() -> None:
    assert (
        convert_source_to_text(b'<meta charset="utf-8"><title>\xff\xfe broken')
        == '<meta charset="utf-8"><title> broken'
    )


@hypothesis.given(raw_source=st.binary(max_size=200))
def test_convert_source_to_text_returns_text_for_any_input(raw_source: bytes) -> None:
    assert isinstance(convert_source_to_text(raw_source), str)
