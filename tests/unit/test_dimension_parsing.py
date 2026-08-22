import typing

import hypothesis
import hypothesis.strategies as st
import pytest

from meta_tags_parser.snippets import _parse_dimension


UNICODE_DIGITS: typing.Final = st.characters(whitelist_categories=["Nd"])
EXPECTED_DIMENSION_EXAMPLES: typing.Final[tuple[tuple[str, int], ...]] = (
    ("", 0),
    ("   ", 0),
    ("123", 123),
    (" 640 ", 640),
    ("0", 0),
    ("abc", 0),
    ("12.5", 0),
    ("-12", 0),
    ("١٢٣", 0),
    ("٥", 0),
    ("²", 0),
    ("1200px", 0),
)


@pytest.mark.parametrize(("dimension_text", "expected_value"), EXPECTED_DIMENSION_EXAMPLES)
def test_parse_dimension_examples(dimension_text: str, expected_value: int) -> None:
    assert _parse_dimension(dimension_text) == expected_value


@hypothesis.given(
    dimension_text=st.one_of(
        st.integers(min_value=0, max_value=100_000).map(str),
        st.text(alphabet=UNICODE_DIGITS, min_size=1, max_size=8),
        st.text(max_size=8),
    )
)
def test_parse_dimension_matches_the_ascii_digit_rule(dimension_text: str) -> None:
    cleaned_text: typing.Final[str] = dimension_text.strip()

    parsed_value: typing.Final[int] = _parse_dimension(dimension_text)

    assert parsed_value == (int(cleaned_text) if cleaned_text.isascii() and cleaned_text.isdigit() else 0)
    assert parsed_value >= 0
