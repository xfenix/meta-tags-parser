"""Main parsing module."""
from __future__ import annotations
import re
import typing

from . import settings, structs


if typing.TYPE_CHECKING:
    from collections.abc import KeysView


_RE_FLAGS: re.RegexFlag = re.IGNORECASE | re.MULTILINE | re.DOTALL
TITLE_TAG_RE: typing.Final[re.Pattern] = re.compile(r"<title>\s*(.*?)\s*</title>", flags=_RE_FLAGS)
META_TAGS_RE: typing.Final[re.Pattern] = re.compile(r"<meta([^>]*)>", flags=_RE_FLAGS)
TAG_ATTRS_RE: typing.Final[re.Pattern] = re.compile(
    r"(?:([^\s=\"']+)\s*=\s*(?:(?:[\"'](.*?)[\"'])|[^\s\"']*))", flags=_RE_FLAGS
)


def _extract_social_tags_from_precusor(
    all_tech_attrs: list[dict[str, structs.ValuesGroup]],
    media_type: typing.Literal[structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER],
) -> list[structs.OneMetaTag]:
    possible_settings_for_parsing: dict[str, str | tuple] = settings.SETTINGS_FOR_SOCIAL_MEDIA[media_type]
    output_buffer: list[structs.OneMetaTag] = []
    for one_attr_group in all_tech_attrs:
        og_tag_name: str = ""
        tech_keys: KeysView[str] = one_attr_group.keys()
        for attr_name in possible_settings_for_parsing["prop"]:
            if attr_name in tech_keys and one_attr_group[attr_name].normalized.startswith(
                possible_settings_for_parsing["prefix"]
            ):
                og_tag_name = one_attr_group[attr_name].normalized.replace(
                    str(possible_settings_for_parsing["prefix"]), ""
                )
            if og_tag_name and "content" in tech_keys and one_attr_group["content"].original:
                output_buffer.append(structs.OneMetaTag(name=og_tag_name, value=one_attr_group["content"].original))
                break
    return output_buffer


def _extract_basic_tags_from_precursor(
    all_tech_attrs: list[dict[str, structs.ValuesGroup]]
) -> list[structs.OneMetaTag]:
    output_buffer: list[structs.OneMetaTag] = []
    for one_attr_group in all_tech_attrs:
        tech_keys: KeysView[str] = one_attr_group.keys()

        if len(output_buffer) == len(settings.BASIC_META_TAGS):
            break
        output_buffer.extend(
            structs.OneMetaTag(
                name=one_ordinary_meta_tag,
                value=one_attr_group["content"].original,
            )
            for one_ordinary_meta_tag in settings.BASIC_META_TAGS
            if (
                "name" in tech_keys
                and one_attr_group["name"].normalized == one_ordinary_meta_tag
                and "content" in one_attr_group
                and one_attr_group["content"].original
            )
        )
    return output_buffer


def _extract_all_other_tags_from_precursor(
    all_tech_attrs: list[dict[str, structs.ValuesGroup]]
) -> list[structs.OneMetaTag]:
    output_buffer: list[structs.OneMetaTag] = []
    for one_attr_group in all_tech_attrs:
        tech_keys: KeysView[str] = one_attr_group.keys()

        should_we_skip: bool = False
        for one_config in settings.SETTINGS_FOR_SOCIAL_MEDIA.values():
            for attr_name in one_config["prop"]:
                if attr_name in tech_keys and one_attr_group[attr_name].normalized.startswith(one_config["prefix"]):
                    should_we_skip = True
                    break
        if should_we_skip:
            continue

        if "name" in tech_keys:
            if one_attr_group["name"].normalized in settings.BASIC_META_TAGS:
                continue
            if "content" in one_attr_group and one_attr_group["content"].original:
                output_buffer.append(
                    structs.OneMetaTag(
                        name=one_attr_group["name"].normalized,
                        value=one_attr_group["content"].original,
                    )
                )
    return output_buffer


def _prepare_normalized_meta_attrs(
    source_code: str,
) -> list[dict[str, structs.ValuesGroup]]:
    raw_tags_attrs: list[str] = META_TAGS_RE.findall(source_code)
    normalized_meta_attrs: list[dict[str, structs.ValuesGroup]] = []
    for one_raw_attrs_row in raw_tags_attrs:
        prepared_attrs: dict[str, structs.ValuesGroup] = {}
        for attr_key, attr_value in dict(TAG_ATTRS_RE.findall(one_raw_attrs_row)).items():
            prepared_attrs[attr_key.lower().strip()] = structs.ValuesGroup(
                original=attr_value, normalized=attr_value.lower().strip()
            )
        normalized_meta_attrs.append(prepared_attrs)
    return normalized_meta_attrs


def parse_meta_tags_from_source(
    source_code: str,
    what_to_parse: tuple[structs.WhatToParse, ...] = settings.DEFAULT_PARSE_GROUP,
) -> structs.TagsGroup:
    """Parse meta tags from source code."""
    page_title: str = ""
    basic_meta_tags: list[structs.OneMetaTag] = []
    open_graph_meta_tags: list[structs.OneMetaTag] = []
    twitter_meta_tags: list[structs.OneMetaTag] = []
    other_meta_tags: list[structs.OneMetaTag] = []

    if structs.WhatToParse.TITLE in what_to_parse:
        possible_match: re.Match[str] | None = TITLE_TAG_RE.search(source_code)
        if possible_match:
            possible_groups: tuple[typing.Any, ...] = possible_match.groups()
            if possible_groups:
                page_title = str(possible_groups[0])

    if any(
        one in what_to_parse
        for one in (
            structs.WhatToParse.OPEN_GRAPH,
            structs.WhatToParse.TWITTER,
            structs.WhatToParse.BASIC,
            structs.WhatToParse.OTHER,
        )
    ):
        normalized_meta_attrs: list[dict[str, structs.ValuesGroup]] = _prepare_normalized_meta_attrs(source_code)

        if structs.WhatToParse.OPEN_GRAPH in what_to_parse:
            open_graph_meta_tags = _extract_social_tags_from_precusor(
                normalized_meta_attrs, structs.WhatToParse.OPEN_GRAPH
            )

        if structs.WhatToParse.TWITTER in what_to_parse:
            twitter_meta_tags = _extract_social_tags_from_precusor(
                normalized_meta_attrs, structs.WhatToParse.TWITTER
            )

        if structs.WhatToParse.BASIC in what_to_parse:
            basic_meta_tags = _extract_basic_tags_from_precursor(normalized_meta_attrs)

        if structs.WhatToParse.OTHER in what_to_parse:
            other_meta_tags = _extract_all_other_tags_from_precursor(normalized_meta_attrs)

    return structs.TagsGroup(
        title=page_title,
        basic=basic_meta_tags,
        open_graph=open_graph_meta_tags,
        twitter=twitter_meta_tags,
        other=other_meta_tags,
    )


__all__ = ["parse_meta_tags_from_source"]
