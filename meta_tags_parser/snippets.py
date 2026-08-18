import dataclasses
import typing

from . import parse, structs


def _parse_dimension(dimension_text: str) -> int:
    cleaned_text: typing.Final[str] = dimension_text.strip()
    if not cleaned_text:
        return 0
    if not cleaned_text.isascii() or not cleaned_text.isdigit():
        return 0
    return int(cleaned_text)


def parse_snippets_from_source(
    source_code: str | bytes,
    *,
    options: structs.SettingsFromUser | None = None,
) -> structs.SnippetGroup:
    active_options: typing.Final[structs.SettingsFromUser] = parse.resolve_active_options(options)
    snippets_options: typing.Final[structs.SettingsFromUser] = dataclasses.replace(
        active_options,
        what_to_parse=(structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER),
    )
    parsed_group: typing.Final[structs.TagsGroup] = parse.parse_meta_tags_from_source(
        source_code,
        options=snippets_options,
    )
    prepared_group_data: typing.Final[dict[str, structs.SocialMediaSnippet]] = {}
    social_name: str
    parsed_tags: list[structs.OneMetaTag]
    for social_name, parsed_tags in (
        ("twitter", parsed_group.twitter),
        ("open_graph", parsed_group.open_graph),
    ):
        prepared_snippet_data: dict[str, typing.Any] = {}
        one_meta_tag: structs.OneMetaTag
        for one_meta_tag in parsed_tags:
            snippet_field_name: str = one_meta_tag.normalized_name
            if snippet_field_name not in structs.WHAT_ATTRS_IN_SOCIAL_MEDIA_SNIPPET:
                continue
            # og/twitter allow repeated tags (multiple images for example), the first one is the primary one
            if snippet_field_name in prepared_snippet_data:
                continue
            prepared_snippet_data[snippet_field_name] = (
                _parse_dimension(one_meta_tag.value)
                if snippet_field_name in structs.DIMENSION_SNIPPET_FIELDS
                else one_meta_tag.value
            )
        prepared_group_data[social_name] = structs.SocialMediaSnippet(**prepared_snippet_data)
    return structs.SnippetGroup(**prepared_group_data)
