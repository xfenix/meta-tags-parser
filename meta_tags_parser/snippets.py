import dataclasses
import typing

from . import structs
from .parse import parse_meta_tags_from_source


def _normalize_dimension(dimension_text: str) -> int:
    try:
        return int(dimension_text)
    except ValueError:
        return 0


_SNIPPET_RULES: typing.Final[
    dict[str, typing.Callable[[structs.SocialMediaSnippet, str], structs.SocialMediaSnippet]]
] = {
    "title": lambda snippet_data, tag_value: dataclasses.replace(snippet_data, title=tag_value),
    "description": lambda snippet_data, tag_value: dataclasses.replace(snippet_data, description=tag_value),
    "url": lambda snippet_data, tag_value: dataclasses.replace(snippet_data, url=tag_value),
    "image": lambda snippet_data, tag_value: dataclasses.replace(snippet_data, image=tag_value),
    "image:width": lambda snippet_data, tag_value: dataclasses.replace(
        snippet_data, image_width=_normalize_dimension(tag_value)
    ),
    "image:height": lambda snippet_data, tag_value: dataclasses.replace(
        snippet_data, image_height=_normalize_dimension(tag_value)
    ),
}


def _merge_snippet_tag(
    snippet_object: structs.SocialMediaSnippet, one_meta_tag: structs.OneMetaTag
) -> structs.SocialMediaSnippet:
    rule = _SNIPPET_RULES.get(one_meta_tag.name)
    if rule is None:
        return snippet_object
    return rule(snippet_object, one_meta_tag.value)


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
        snippet_object: structs.SocialMediaSnippet = structs.SocialMediaSnippet()
        one_meta_tag: structs.OneMetaTag
        for one_meta_tag in parsed_tags:
            snippet_object = _merge_snippet_tag(snippet_object, one_meta_tag)
        if social_name == "twitter":
            result_group = dataclasses.replace(result_group, twitter=snippet_object)
        else:
            result_group = dataclasses.replace(result_group, open_graph=snippet_object)
    return result_group


__all__ = ["parse_snippets_from_source"]
