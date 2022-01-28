"""Snippets helper functions."""
from .parse import parse_meta_tags_from_source, settings, structs


def parse_snippets_from_source(source_code: str) -> structs.SnippetGroup:
    """Parse snippets from source code.

    This function use «ugly» magic like getattr, setattr.
    This is sad, but i don't find at the bottom of my mind a better solution at the moment.
    If you have a more reasonable solution — feel free to push me, I will be grateful for any advice.
    """
    tags_groups: structs.TagsGroup = parse_meta_tags_from_source(
        source_code, (structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER)
    )
    prepared_result: structs.SnippetGroup = structs.SnippetGroup()
    sm_group: str
    one_tag: structs.OneMetaTag
    for sm_group in settings.SOCIAL_MEDIA_SNIPPET_GROUPS:
        prepared_snippet: structs.SocialMediaSnippet = getattr(prepared_result, sm_group)
        for one_tag in getattr(tags_groups, sm_group):
            if one_tag.name in settings.SOCIAL_MEDIA_SNIPPET_WHAT_ATTRS_TO_COPY:
                # any attrs like "image:width" will be converted to
                # underscored versions, like this — "image_width"
                setattr(prepared_snippet, one_tag.name.replace(":", "_"), one_tag.value)
    return prepared_result


__all__ = ["parse_snippets_from_source"]
