import typing

import hypothesis
import hypothesis.strategies as st
import pytest

from meta_tags_parser import parse_snippets_from_source
from meta_tags_parser.snippets import _parse_dimension


@pytest.mark.parametrize(
    ("dimension_text", "expected_width"),
    [
        ("", 0),
        ("123", 123),
        ("abc", 0),
        ("\u0665", 0),
        ("²", 0),
    ],
)
def test_parse_image_width(dimension_text: str, expected_width: int) -> None:
    html_text: typing.Final = f'<meta property="twitter:image:width" content="{dimension_text}">'
    parsed_snippets: typing.Final = parse_snippets_from_source(html_text)
    assert parsed_snippets.twitter.image_width == expected_width


UNICODE_DIGITS: typing.Final = st.characters(whitelist_categories=["Nd"])


@hypothesis.settings(max_examples=20)
@hypothesis.given(
    dimension_text=st.one_of(
        st.integers(min_value=0, max_value=100).map(str),
        st.text(alphabet=UNICODE_DIGITS, min_size=1, max_size=8),
        st.text(alphabet=st.characters(blacklist_characters='<>"'), min_size=1, max_size=8),
    )
)
def test_parse_image_width_property(dimension_text: str) -> None:
    html_text: typing.Final = f'<meta property="twitter:image:width" content="{dimension_text}">' 
    parsed_snippets: typing.Final = parse_snippets_from_source(html_text)
    cleaned_text: typing.Final[str] = dimension_text.strip()
    expected_width: typing.Final[int] = int(cleaned_text) if cleaned_text.isascii() and cleaned_text.isdigit() else 0
    assert parsed_snippets.twitter.image_width == expected_width


def test_parse_dimension_empty_text_returns_zero() -> None:
    assert _parse_dimension("   ") == 0
