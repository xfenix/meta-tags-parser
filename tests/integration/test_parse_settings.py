import typing

import pytest

from meta_tags_parser import (
    parse_meta_tags_from_source,
    parse_snippets_from_source,
    set_settings_for_meta_tags,
    structs,
)


FULL_PAGE_FIXTURE: typing.Final = (
    "<html><head>"
    "<title>Site Title</title>"
    '<meta name="description" content="Example description">'
    '<meta property="og:title" content="OG Title">'
    '<meta name="twitter:title" content="Twitter Title">'
    '<meta name="generator" content="Hand made">'
    "</head></html>"
)
BODY_TAGS_PAGE_FIXTURE: typing.Final = (
    '<html><head><title>Head title</title></head><body><meta property="og:title" content="Body title"></body></html>'
)


@pytest.mark.parametrize(
    ("requested_parts", "expected_filled_fields"),
    [
        ((structs.WhatToParse.TITLE,), {"title"}),
        ((structs.WhatToParse.BASIC,), {"basic"}),
        ((structs.WhatToParse.OPEN_GRAPH,), {"open_graph"}),
        ((structs.WhatToParse.TWITTER,), {"twitter"}),
        ((structs.WhatToParse.OTHER,), {"other"}),
        ((structs.WhatToParse.TITLE, structs.WhatToParse.OPEN_GRAPH), {"title", "open_graph"}),
        (
            (structs.WhatToParse.BASIC, structs.WhatToParse.TWITTER, structs.WhatToParse.OTHER),
            {"basic", "twitter", "other"},
        ),
    ],
)
def test_what_to_parse_limits_the_result(
    requested_parts: tuple[structs.WhatToParse, ...], expected_filled_fields: set[str]
) -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        FULL_PAGE_FIXTURE, options=structs.SettingsFromUser(what_to_parse=requested_parts)
    )

    filled_fields: typing.Final[set[str]] = {
        one_field_name
        for one_field_name in ("title", "basic", "open_graph", "twitter", "other")
        if getattr(parse_result, one_field_name)
    }
    assert filled_fields == expected_filled_fields


def test_global_settings_are_used_and_can_be_restored() -> None:
    set_settings_for_meta_tags(structs.SettingsFromUser(what_to_parse=(structs.WhatToParse.TITLE,)))

    limited_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(FULL_PAGE_FIXTURE)

    assert limited_result == structs.TagsGroup(title="Site Title")

    set_settings_for_meta_tags(structs.DEFAULT_SETTINGS_FROM_USER)
    restored_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(FULL_PAGE_FIXTURE)

    assert restored_result.basic
    assert restored_result.open_graph
    assert restored_result.twitter
    assert restored_result.other


def test_explicit_options_win_over_global_settings() -> None:
    set_settings_for_meta_tags(structs.SettingsFromUser(what_to_parse=(structs.WhatToParse.TITLE,)))

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        FULL_PAGE_FIXTURE, options=structs.SettingsFromUser(what_to_parse=(structs.WhatToParse.OPEN_GRAPH,))
    )

    assert parse_result.open_graph == [structs.OneMetaTag(name="title", value="OG Title")]
    assert parse_result.title == ""


def test_snippets_follow_global_settings_too() -> None:
    """Snippets used to silently ignore set_settings_for_meta_tags and always use the defaults."""
    set_settings_for_meta_tags(structs.SettingsFromUser(optimize_input=False))

    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(BODY_TAGS_PAGE_FIXTURE)

    assert snippet_result.open_graph.title == "Body title"


def test_snippets_ignore_body_tags_with_default_settings() -> None:
    assert parse_snippets_from_source(BODY_TAGS_PAGE_FIXTURE).open_graph.title == ""
