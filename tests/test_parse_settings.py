import typing

import pytest

from meta_tags_parser import (
    parse_meta_tags_from_source,
    parse_snippets_from_source,
    set_settings_for_meta_tags,
    structs,
)
from tests import factories


HEAD_OPENING_MARKUP: typing.Final = "<html><head>"
TITLE_MARKUP: typing.Final = "<title>Site Title</title>"
FULL_PAGE_FIXTURE: typing.Final = (
    f"{HEAD_OPENING_MARKUP}{TITLE_MARKUP}"
    '<meta name="description" content="Example description">'
    '<meta property="og:title" content="OG Title">'
    '<meta name="twitter:title" content="Twitter Title">'
    '<meta name="generator" content="Hand made">'
    "</head></html>"
)
BODY_TAGS_PAGE_FIXTURE: typing.Final = (
    '<html><head><title>Head title</title></head><body><meta property="og:title" content="Body title"></body></html>'
)
EARLY_SOCIAL_TAG_MARKUP: typing.Final = '<meta property="og:title" content="Early title">'
LATE_SOCIAL_TAG_MARKUP: typing.Final = '<meta property="og:description" content="Late description">'
PADDING_LENGTH: typing.Final = 300
GENERATED_SETTINGS_COUNT: typing.Final = 40
PARSED_FIELD_NAMES: typing.Final[tuple[tuple[structs.WhatToParse, str], ...]] = (
    (structs.WhatToParse.TITLE, "title"),
    (structs.WhatToParse.BASIC, "basic"),
    (structs.WhatToParse.OPEN_GRAPH, "open_graph"),
    (structs.WhatToParse.TWITTER, "twitter"),
    (structs.WhatToParse.OTHER, "other"),
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


def test_hard_limit_chars_cuts_the_markup_that_is_looked_at() -> None:
    limited_settings: typing.Final = structs.SettingsFromUser(
        hard_limit_chars=len(HEAD_OPENING_MARKUP) + len(TITLE_MARKUP)
    )

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        FULL_PAGE_FIXTURE, options=limited_settings
    )

    assert parse_result == structs.TagsGroup(title="Site Title")


def test_hard_limit_larger_than_the_head_keeps_every_tag() -> None:
    generous_settings: typing.Final = structs.SettingsFromUser(hard_limit_chars=10_000)

    assert parse_meta_tags_from_source(FULL_PAGE_FIXTURE, options=generous_settings) == parse_meta_tags_from_source(
        FULL_PAGE_FIXTURE
    )


def test_fallback_limit_decides_when_the_page_has_no_boundary_tag() -> None:
    """Without a head or body tag there is nothing to cut at, so the fallback limit is the whole window."""
    page_fixture: typing.Final[str] = f"{EARLY_SOCIAL_TAG_MARKUP}{'x' * PADDING_LENGTH}{LATE_SOCIAL_TAG_MARKUP}"
    fallback_settings: typing.Final = structs.SettingsFromUser(
        fallback_limit_chars=len(EARLY_SOCIAL_TAG_MARKUP) + PADDING_LENGTH
    )

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_fixture, options=fallback_settings)

    assert parse_result.open_graph == [structs.OneMetaTag(name="title", value="Early title")]


def test_boundary_beyond_max_scan_chars_is_not_looked_for() -> None:
    page_fixture: typing.Final[str] = (
        f"<html><head>{EARLY_SOCIAL_TAG_MARKUP}{'x' * PADDING_LENGTH}{LATE_SOCIAL_TAG_MARKUP}</head><body>"
    )
    narrow_settings: typing.Final = structs.SettingsFromUser(
        max_scan_chars=len(EARLY_SOCIAL_TAG_MARKUP),
        fallback_limit_chars=len(EARLY_SOCIAL_TAG_MARKUP) + PADDING_LENGTH,
    )

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_fixture, options=narrow_settings)

    assert parse_result.open_graph == [structs.OneMetaTag(name="title", value="Early title")]


def test_custom_boundary_tags_change_where_scanning_stops() -> None:
    custom_settings: typing.Final = structs.SettingsFromUser(boundary_tags=("</title>", "<article"))

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        FULL_PAGE_FIXTURE, options=custom_settings
    )

    assert parse_result == structs.TagsGroup(title="Site Title")


def test_multi_character_lowercasing_does_not_shift_the_boundary() -> None:
    """U+0130 lowercases into two characters, a window computed on a lowered copy would cut too early."""
    turkish_value: typing.Final = "İ" * 10
    page_fixture: typing.Final[str] = (
        f'<html><head><meta name="geo" content="{turkish_value}"></head>'
        '<body><meta property="og:title" content="Body title"></body></html>'
    )

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_fixture)

    assert parse_result.other == [structs.OneMetaTag(name="geo", value=turkish_value)]
    assert parse_result.open_graph == []


@pytest.mark.parametrize("generated_settings", factories.SettingsFromUserFactory.batch(GENERATED_SETTINGS_COUNT))
def test_generated_settings_never_fill_parts_that_were_not_requested(
    generated_settings: structs.SettingsFromUser,
) -> None:
    requested_parts: typing.Final[frozenset[structs.WhatToParse]] = frozenset(generated_settings.what_to_parse)

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        FULL_PAGE_FIXTURE, options=generated_settings
    )

    for one_part, one_field_name in PARSED_FIELD_NAMES:
        if one_part not in requested_parts:
            assert not getattr(parse_result, one_field_name)
