import typing

from . import structs
from .parse import parse_meta_tags_from_source


def _parse_dimension(dimension_text: str) -> int:
    cleaned_text: typing.Final[str] = dimension_text.strip()
    if not cleaned_text:
        return 0
    if not cleaned_text.isascii() or not cleaned_text.isdigit():
        return 0
    return int(cleaned_text)


def parse_snippets_from_source(source_code: str) -> structs.SnippetGroup:
    parsed_group: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        source_code, (structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER)
    )
    prepared_group_data: dict[str, structs.SocialMediaSnippet] = {}
    social_name: str
    parsed_tags: list[structs.OneMetaTag]
    for social_name, parsed_tags in (
        ("twitter", parsed_group.twitter),
        ("open_graph", parsed_group.open_graph),
    ):
        prepared_snippet_data: dict[str, typing.Any] = {}
        structs.SocialMediaSnippet()
        one_meta_tag: structs.OneMetaTag
        for one_meta_tag in parsed_tags:
            if one_meta_tag.name not in structs.WHAT_ATTRS_IN_SOCIAL_MEDIA_SNIPPET:
                continue
            prepared_snippet_data[one_meta_tag.name] = (
                _parse_dimension(one_meta_tag.value) if one_meta_tag.name.startswith("image:") else one_meta_tag.value
            )
        prepared_group_data[social_name] = structs.SocialMediaSnippet(**prepared_snippet_data)
    return structs.SnippetGroup(**prepared_group_data)
