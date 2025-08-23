import re
import typing

import hypothesis
import hypothesis.strategies as st

from meta_tags_parser import parse_meta_tags_from_source, structs


def test_parse_handles_malformed_html() -> None:
    html_source = """
    <html><head>
    <meta name="description" content="Valid description">
    <meta property="og:title" content="OG Title">
    <meta name="keywords" content="foo,bar"
    </head></html>
    """
    parse_result = parse_meta_tags_from_source(html_source)
    assert structs.OneMetaTag(name="description", value="Valid description") in parse_result.basic
    assert structs.OneMetaTag(name="title", value="OG Title") in parse_result.open_graph


@hypothesis.settings(max_examples=20)
@hypothesis.given(
    property_attribute=st.from_regex(re.compile("property", re.IGNORECASE), fullmatch=True),
    name_attribute=st.from_regex(re.compile("name", re.IGNORECASE), fullmatch=True),
    content_attribute=st.from_regex(re.compile("content", re.IGNORECASE), fullmatch=True),
)
def test_attribute_normalization_in_parser(
    property_attribute: str, name_attribute: str, content_attribute: str
) -> None:
    html_source: typing.Final = (
        f'<meta {property_attribute}="OG:TITLE" {content_attribute}="HELLO">'
        f'<meta {name_attribute}="TWITTER:DESCRIPTION" {content_attribute}="WORLD">'
    )
    parse_result: typing.Final = parse_meta_tags_from_source(html_source)
    assert structs.OneMetaTag(name="title", value="HELLO") in parse_result.open_graph
    assert structs.OneMetaTag(name="description", value="WORLD") in parse_result.twitter
