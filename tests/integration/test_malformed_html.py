import typing

import hypothesis
import hypothesis.strategies as st
import pytest

from meta_tags_parser import parse_meta_tags_from_source, parse_snippets_from_source, structs


BROKEN_TEXT_ALPHABET: typing.Final = st.characters(blacklist_categories=("Cc", "Cs"), blacklist_characters='<>"&=/')


def test_unclosed_tag_does_not_hide_earlier_tags() -> None:
    page_fixture: typing.Final = """
    <html><head>
    <meta name="description" content="Valid description">
    <meta property="og:title" content="OG Title">
    <meta name="keywords" content="foo,bar"
    </head></html>
    """

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_fixture)

    assert structs.OneMetaTag(name="description", value="Valid description") in parse_result.basic
    assert structs.OneMetaTag(name="title", value="OG Title") in parse_result.open_graph


@pytest.mark.parametrize(
    "page_fixture",
    [
        "",
        "   ",
        "<html>",
        "not html at all",
        "<html><head><title></title></head></html>",
        "<!-- <meta property='og:title' content='commented out'> -->",
        "<html><head><meta/></head>",
        "<html><head><meta content='no name at all'></head>",
        "\ufeff<html><head><title>with bom</title></head>",
    ],
)
def test_degenerate_pages_never_raise(page_fixture: str) -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_fixture)

    assert parse_result.open_graph == []
    assert parse_result.twitter == []
    assert parse_snippets_from_source(page_fixture) == structs.SnippetGroup()


def test_leading_byte_order_mark_does_not_break_the_title() -> None:
    assert parse_meta_tags_from_source("\ufeff<html><head><title>with bom</title></head>").title == "with bom"


@hypothesis.given(title_value=st.text(alphabet=BROKEN_TEXT_ALPHABET, max_size=20))
def test_attribute_without_closing_quote_yields_no_social_tags(title_value: str) -> None:
    page_fixture: typing.Final = f"""
    <meta property="og:title" value="{title_value}>
    <meta property=twitter:description" value="{title_value}">
    """

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_fixture)

    assert parse_result.open_graph == []
    assert parse_result.twitter == []


@hypothesis.settings(max_examples=50)
@hypothesis.given(page_fixture=st.text(max_size=300))
def test_arbitrary_text_is_parsed_without_errors(page_fixture: str) -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        f'<meta property="og:title" content="known value">{page_fixture}'
    )

    assert isinstance(parse_result, structs.TagsGroup)
    for one_meta_tag in (*parse_result.basic, *parse_result.open_graph, *parse_result.twitter, *parse_result.other):
        assert one_meta_tag.value
        assert one_meta_tag.name == one_meta_tag.name.strip()


@pytest.mark.parametrize("declared_charset", ["base64", "hex", "zip", "idna", "unknown-charset"])
def test_bytes_with_unusable_declared_charset_are_still_parsed(declared_charset: str) -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        f'<html><head><meta charset="{declared_charset}"><title>Still here</title></head></html>'.encode()
    )

    assert parse_result.title == "Still here"
