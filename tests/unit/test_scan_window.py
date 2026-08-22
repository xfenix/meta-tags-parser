import typing

import hypothesis
import hypothesis.strategies as st
import pytest

from meta_tags_parser import structs
from meta_tags_parser.parse import _extract_html_scan_window
from tests import factories


SAFE_HTML_TEXT: typing.Final = st.text(alphabet=st.characters(blacklist_characters='<>"'), min_size=1, max_size=100)
GENERATED_SETTINGS_COUNT: typing.Final = 40


@pytest.mark.parametrize(
    ("html_source", "expected_window"),
    [
        ("<head><title>x</title></head><body>ignored", "<head><title>x</title></head>"),
        ("<HEAD><TITLE>x</TITLE></HEAD><BODY>ignored", "<HEAD><TITLE>x</TITLE></HEAD>"),
        ("<head><title>x</title><body>ignored", "<head><title>x</title>"),
        ("<head><title>x</title>", "<head><title>x</title>"),
    ],
)
def test_scan_window_cuts_at_the_first_boundary(html_source: str, expected_window: str) -> None:
    assert _extract_html_scan_window(html_source, structs.DEFAULT_SETTINGS_FROM_USER) == expected_window


def test_scan_window_respects_hard_limit_chars() -> None:
    expected_length: typing.Final = 12
    limited_settings: typing.Final = structs.SettingsFromUser(hard_limit_chars=expected_length)

    scan_window: typing.Final[str] = _extract_html_scan_window(
        "<head><title>a long enough title</title></head><body>", limited_settings
    )

    assert scan_window == "<head><title"
    assert len(scan_window) == expected_length


def test_scan_window_keeps_whole_head_when_hard_limit_is_larger() -> None:
    generous_settings: typing.Final = structs.SettingsFromUser(hard_limit_chars=10_000)

    scan_window: typing.Final[str] = _extract_html_scan_window("<head><title>x</title></head><body>", generous_settings)

    assert scan_window == "<head><title>x</title></head>"


def test_scan_window_applies_hard_limit_on_the_fallback_path() -> None:
    fallback_settings: typing.Final = structs.SettingsFromUser(
        fallback_limit_chars=200, max_scan_chars=200, hard_limit_chars=10
    )

    scan_window: typing.Final[str] = _extract_html_scan_window("<html>" + "x" * 300, fallback_settings)

    assert scan_window == "<html>xxxx"


def test_scan_window_falls_back_when_no_boundary_is_found() -> None:
    expected_length: typing.Final = 50
    fallback_settings: typing.Final = structs.SettingsFromUser(fallback_limit_chars=expected_length, max_scan_chars=200)

    scan_window: typing.Final[str] = _extract_html_scan_window("<html>" + "x" * 300, fallback_settings)

    assert len(scan_window) == expected_length


def test_scan_window_ignores_boundary_beyond_max_scan_chars() -> None:
    expected_length: typing.Final = 80
    long_head: typing.Final[str] = "<head>" + "y" * 500 + "</head><body>"
    narrow_settings: typing.Final = structs.SettingsFromUser(max_scan_chars=100, fallback_limit_chars=expected_length)

    scan_window: typing.Final[str] = _extract_html_scan_window(long_head, narrow_settings)

    assert len(scan_window) == expected_length


def test_scan_window_supports_custom_boundary_tags() -> None:
    custom_settings: typing.Final = structs.SettingsFromUser(boundary_tags=("</title>", "<article"))

    scan_window: typing.Final[str] = _extract_html_scan_window(
        "<head><title>x</title><meta name='a' content='b'></head>", custom_settings
    )

    assert scan_window == "<head><title>x</title>"


def test_scan_window_is_not_shifted_by_multi_character_lowercasing() -> None:
    """U+0130 lowercases into two characters, offsets computed on a lowered copy must not shift."""
    html_source: typing.Final = '<head><meta name="geo" content="İİİİİİİİİİ"></head><body>ignored'

    scan_window: typing.Final[str] = _extract_html_scan_window(html_source, structs.DEFAULT_SETTINGS_FROM_USER)

    assert scan_window.endswith("</head>")
    assert "<body" not in scan_window


@hypothesis.given(description_text=SAFE_HTML_TEXT)
def test_scan_window_stops_at_head_end(description_text: str) -> None:
    scan_window: typing.Final[str] = _extract_html_scan_window(
        f'<html><head><meta name="description" content="{description_text}"></head><body>ignored',
        structs.DEFAULT_SETTINGS_FROM_USER,
    )

    assert scan_window.endswith("</head>")
    assert "<body" not in scan_window


@hypothesis.given(html_source=st.text(max_size=500))
@pytest.mark.parametrize("generated_settings", factories.SettingsFromUserFactory.batch(GENERATED_SETTINGS_COUNT))
def test_scan_window_always_returns_a_prefix(html_source: str, generated_settings: structs.SettingsFromUser) -> None:
    scan_window: typing.Final[str] = _extract_html_scan_window(html_source, generated_settings)

    assert html_source.startswith(scan_window)
    if generated_settings.hard_limit_chars is not None:
        assert len(scan_window) <= generated_settings.hard_limit_chars
