"""Main parsing module."""
import re
import typing
from collections.abc import KeysView

from . import structs


TITLE_TAG_RE: typing.Final[re.Pattern] = re.compile("<title>\s*(.*?)\s*</title>")
META_TAGS_RE: typing.Final[re.Pattern] = re.compile("<meta([^>]*)>")
TAG_ATTRS_RE: typing.Final[re.Pattern] = re.compile("(?:([^\s=\"']+)\s*=\s*(?:(?:[\"'](.*?)[\"'])|[^\s\"']*))")


def _extract_social_tags_from_precusor(
    all_tech_attrs: list[dict[str, structs.ValuesGroup]],
    media_type: typing.Literal[structs.WhatToParse.OG, structs.WhatToParse.TWITTER],
) -> list[structs.OneMetaTag]:
    possible_settings_for_parsing: dict[str, str] = structs.SETTINGS_FOR_SOCIAL_MEDIA[media_type]
    output_buffer: list[structs.OneMetaTag] = []
    for one_attr_group in all_tech_attrs:
        og_tag_name: str = ""
        tech_keys: KeysView[str] = one_attr_group.keys()
        if possible_settings_for_parsing["prop"] in tech_keys and one_attr_group[
            possible_settings_for_parsing["prop"]
        ].normalized.startswith(possible_settings_for_parsing["prefix"]):
            og_tag_name = one_attr_group[possible_settings_for_parsing["prop"]].normalized.replace(
                possible_settings_for_parsing["prefix"], ""
            )
        if og_tag_name and "content" in tech_keys and one_attr_group["content"].original:
            output_buffer.append(structs.OneMetaTag(name=og_tag_name, value=one_attr_group["content"].original))
    return output_buffer


def _extract_basic_tags_from_precursor(
    all_tech_attrs: list[dict[str, structs.ValuesGroup]]
) -> list[structs.OneMetaTag]:
    output_buffer: list[structs.OneMetaTag] = []
    for one_attr_group in all_tech_attrs:
        tech_keys: KeysView[str] = one_attr_group.keys()

        if len(output_buffer) == len(structs.BASIC_META_TAGS):
            break

        for one_ordinary_meta_tag in structs.BASIC_META_TAGS:
            if (
                "name" in tech_keys
                and one_attr_group["name"].normalized == one_ordinary_meta_tag
                and "content" in one_attr_group
                and one_attr_group["content"].original
            ):
                output_buffer.append(
                    structs.OneMetaTag(
                        name=one_ordinary_meta_tag,
                        value=one_attr_group["content"].original,
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
        for one_config in structs.SETTINGS_FOR_SOCIAL_MEDIA.values():
            if one_config["prop"] in tech_keys and one_attr_group[one_config["prop"]].normalized.startswith(
                one_config["prefix"]
            ):
                should_we_skip = True
                break
        if should_we_skip:
            continue

        if "name" in tech_keys:
            if one_attr_group["name"].normalized in structs.BASIC_META_TAGS:
                continue
            if one_attr_group["content"].original:
                output_buffer.append(
                    structs.OneMetaTag(
                        name=one_attr_group["name"].normalized,
                        value=one_attr_group["content"].original,
                    )
                )
    return output_buffer


def parse_meta_tags_from_source(source_code: str, what_to_parse=structs.DEFAULT_PARSE_GROUP) -> structs.TagsGroup:
    """Parse meta tags from source code."""
    builded_result: structs.TagsGroup = structs.TagsGroup()

    if structs.WhatToParse.TITLE in what_to_parse:
        possible_match: typing.Optional[re.Match] = TITLE_TAG_RE.search(source_code)
        if possible_match:
            possible_groups: tuple[typing.Any, ...] = possible_match.groups()
            if len(possible_groups) > 0:
                builded_result.title = str(possible_groups[0])

    if (
        structs.WhatToParse.OG in what_to_parse
        or structs.WhatToParse.TWITTER in what_to_parse
        or structs.WhatToParse.BASIC in what_to_parse
        or structs.WhatToParse.OTHER in what_to_parse
    ):
        raw_tags_attrs: typing.Final[list] = META_TAGS_RE.findall(source_code)
        normalized_meta_attrs: list[dict[str, structs.ValuesGroup]] = []
        for raw_tag_attrs in raw_tags_attrs:
            prepared_attrs: dict = {}
            for attr_key, attr_value in dict(TAG_ATTRS_RE.findall(raw_tag_attrs)).items():
                prepared_attrs[attr_key.lower().strip()] = structs.ValuesGroup(attr_value, attr_value.lower().strip())
            normalized_meta_attrs.append(prepared_attrs)
        del raw_tag_attrs

        if structs.WhatToParse.OG in what_to_parse:
            builded_result.og = _extract_social_tags_from_precusor(normalized_meta_attrs, structs.WhatToParse.OG)

        if structs.WhatToParse.TWITTER in what_to_parse:
            builded_result.twitter = _extract_social_tags_from_precusor(
                normalized_meta_attrs, structs.WhatToParse.TWITTER
            )

        if structs.WhatToParse.BASIC in what_to_parse:
            builded_result.basic = _extract_basic_tags_from_precursor(normalized_meta_attrs)

        if structs.WhatToParse.OTHER in what_to_parse:
            builded_result.other = _extract_all_other_tags_from_precursor(normalized_meta_attrs)

    return builded_result


__all__ = ["parse_meta_tags_from_source"]
