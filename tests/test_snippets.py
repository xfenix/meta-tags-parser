import typing

import pytest

from meta_tags_parser import parse_snippets_from_source


@pytest.mark.parametrize(
    ("dimension_text", "expected_width"),
    [("123", 123), ("abc", 0)],
)
def test_parse_image_width(dimension_text: str, expected_width: int) -> None:
    html_text: typing.Final = f'<meta property="twitter:image:width" content="{dimension_text}">'
    parsed_snippets: typing.Final = parse_snippets_from_source(html_text)
    assert parsed_snippets.twitter.image_width == expected_width
