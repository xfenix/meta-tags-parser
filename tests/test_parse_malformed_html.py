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


@hypothesis.given(title_value=st.text(), description_value=st.text())
@typing.no_type_check
def test_attribute_normalization_in_parser(title_value: str, description_value: str) -> None:
    html_source: typing.Final = f"""
    <meta property="og:title" value="{title_value}>
    <meta property=twitter:description" value="{description_value}">
    """
    parse_result: typing.Final = parse_meta_tags_from_source(html_source)
    assert parse_result.open_graph == []
    assert parse_result.twitter == []
