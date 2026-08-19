"""The oracle used by the corpus tests needs tests of its own."""

import typing

from tests import reference_parser


def test_reference_stops_at_the_body_start_tag() -> None:
    page_text: typing.Final = (
        "<html><head><title>Head title</title>"
        '<meta property="og:title" content="in head">'
        '<body><meta property="og:title" content="in body">'
    )

    reference_result: typing.Final = reference_parser.extract_reference_tags(page_text)

    assert reference_result.page_title == "Head title"
    assert reference_result.open_graph_tags == [["title", "in head"]]


def test_reference_stops_at_the_head_end_tag() -> None:
    page_text: typing.Final = (
        '<html><head><meta property="og:title" content="in head"></head><meta property="og:title" content="after head">'
    )

    assert reference_parser.extract_reference_tags(page_text).open_graph_tags == [["title", "in head"]]


def test_reference_applies_the_documented_grouping() -> None:
    page_text: typing.Final = (
        "<head>"
        "<title>  padded &amp; escaped  </title>"
        '<meta property="og:title" content="og value">'
        '<meta name="twitter:card" content="summary">'
        '<meta property="twitter:title" content="twitter via property">'
        '<meta name="description" content="first description">'
        '<meta name="description" content="second description">'
        '<meta name="generator" content="hand made">'
        '<meta name="og:audio" content="og via name">'
        '<meta name="image" property="og:image" content="both attributes">'
        '<meta name="empty" content="">'
        "</head>"
    )

    reference_result: typing.Final = reference_parser.extract_reference_tags(page_text)

    assert reference_result.page_title == "padded & escaped"
    assert reference_result.open_graph_tags == [["title", "og value"], ["image", "both attributes"]]
    assert reference_result.twitter_tags == [["card", "summary"], ["title", "twitter via property"]]
    assert reference_result.basic_tags == [["description", "first description"]]
    assert reference_result.other_tags == [["generator", "hand made"], ["og:audio", "og via name"]]


def test_reference_normalizes_windows_newlines() -> None:
    page_text: typing.Final = '<head><meta property="og:description" content="first\r\nsecond"></head>'

    assert reference_parser.extract_reference_tags(page_text).open_graph_tags == [["description", "first\nsecond"]]
