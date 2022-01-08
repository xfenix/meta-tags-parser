"""Snippets helper functions."""
from .parse import parse_meta_tags_from_source, structs


def parse_snippets_from_source(source_code: str) -> structs.SnippetGroup:
    """Parse snippets from source code."""
    tags_groups: structs.TagsGroup = parse_meta_tags_from_source(
        source_code, (structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER)
    )
    prepared_result: structs.SnippetGroup = structs.SnippetGroup()
    sm_group: str
    one_tag: structs.OneMetaTag
    for sm_group in structs.SOCIAL_MEDIA_SNIPPET_GROUPS:
        prepared_snippet: structs.SocialMediaSnippet = getattr(prepared_result, sm_group)
        for one_tag in getattr(tags_groups, sm_group):
            if one_tag.name in structs.SOCIAL_MEDIA_SNIPPET_WHAT_ATTRS_TO_COPY:
                setattr(prepared_snippet, one_tag.name, one_tag.value)
    return prepared_result


__all__ = ["parse_snippets_from_source"]
