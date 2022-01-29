"""Snippets helper functions."""
from .parse import parse_meta_tags_from_source, settings, structs


def parse_snippets_from_source(source_code: str) -> structs.SnippetGroup:
    """Parse snippets from source code.

    This function use «ugly» magic like getattr, setattr.
    This is sad, but i don't find at the bottom of my mind a better solution at the moment.
    If you have a more reasonable solution — feel free to push me, I will be grateful for any advice.
    """
    parsed_data: structs.TagsGroup = parse_meta_tags_from_source(
        source_code, (structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER)
    )
    prepared_result: structs.SnippetGroup = structs.SnippetGroup()
    sm_group: str
    one_tag: structs.OneMetaTag
    for sm_group in ("twitter", "open_graph"):
        new_snippet: structs.SocialMediaSnippet = structs.SocialMediaSnippet()
        for one_tag in getattr(parsed_data, sm_group):
            if one_tag.name in settings.SOCIAL_MEDIA_SNIPPET_WHAT_ATTRS_TO_COPY:
                setattr(new_snippet, one_tag.name.replace(":", "_"), one_tag.value)
        setattr(prepared_result, sm_group, new_snippet)
    return prepared_result


__all__ = ["parse_snippets_from_source"]
