"""Snippets helper functions."""
import dataclasses
import typing

from . import structs
from .parse import parse_meta_tags_from_source


SNIPPET_META_TAGS: typing.Final[tuple[str, ...]] = (
    "title",
    "description",
    "url",
    "image",
    "image:width",
    "image:height",
)


def parse_snippets_from_source(source_code: str) -> structs.SnippetGroup:
    """Parse snippets from source code."""
    parsed_group: structs.TagsGroup = parse_meta_tags_from_source(
        source_code, (structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER)
    )
    result_group: structs.SnippetGroup = structs.SnippetGroup()
    social_name: str
    parsed_tags: list[structs.OneMetaTag]
    for social_name, parsed_tags in (
        ("twitter", parsed_group.twitter),
        ("open_graph", parsed_group.open_graph),
    ):
        snippet_fields: dict[str, str] = {}
        meta_tag: structs.OneMetaTag
        for meta_tag in parsed_tags:
            if meta_tag.name in SNIPPET_META_TAGS:
                snippet_fields[meta_tag.name.replace(":", "_")] = meta_tag.value
        snippet_object = structs.SocialMediaSnippet(**snippet_fields)
        if social_name == "twitter":
            result_group = dataclasses.replace(result_group, twitter=snippet_object)
        else:
            result_group = dataclasses.replace(result_group, open_graph=snippet_object)
    return result_group


__all__ = ["parse_snippets_from_source"]
