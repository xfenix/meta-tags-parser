import contextvars
import typing
from collections.abc import KeysView

from selectolax.lexbor import LexborHTMLParser, LexborNode

from . import structs


_GLOBAL_OPTIONS_HOLDER: typing.Final[contextvars.ContextVar[structs.SettingsFromUser]] = contextvars.ContextVar(
    "options", default=structs.DEFAULT_SETTINGS_FROM_USER
)


def set_settings_for_meta_tags(new_options: structs.SettingsFromUser) -> None:
    """Override default package options."""
    _GLOBAL_OPTIONS_HOLDER.set(new_options)


def _extract_html_scan_window(html_source: str, active_options: structs.SettingsFromUser) -> str:
    lowered_prefix: typing.Final[str] = html_source[: active_options.max_scan_chars].lower()
    found_boundaries: typing.Final[dict[str, int]] = {
        one_boundary_tag: found_position
        for one_boundary_tag in active_options.boundary_tags
        if (found_position := lowered_prefix.find(one_boundary_tag)) != -1
    }
    if not found_boundaries:
        return html_source[: active_options.fallback_limit_chars]
    matched_boundary, earliest_position = min(found_boundaries.items(), key=lambda one_pair: one_pair[1])
    cut_position: typing.Final[int] = (
        earliest_position + len(active_options.boundary_tags[0])
        if matched_boundary == active_options.boundary_tags[0]
        else earliest_position
    )
    if active_options.hard_limit_chars is None:
        return html_source[:cut_position]
    return html_source[: min(cut_position, active_options.hard_limit_chars)]


def _find_social_tag_name(
    one_attr_group: dict[str, structs.ValuesGroup],
    parsing_settings: typing.Mapping[str, str | tuple[str, ...]],
) -> str:
    tech_keys: typing.Final[KeysView[str]] = one_attr_group.keys()
    tag_prefix: typing.Final[str] = str(parsing_settings["prefix"])
    matching_names: typing.Final[list[str]] = [
        one_attr_group[one_prop_name].normalized.replace(tag_prefix, "")
        for one_prop_name in parsing_settings["prop"]
        if one_prop_name in tech_keys and one_attr_group[one_prop_name].normalized.startswith(tag_prefix)
    ]
    return matching_names[0] if matching_names else ""


def _extract_social_tags_from_precursor(
    all_tech_attrs: list[dict[str, structs.ValuesGroup]],
    media_type: typing.Literal[structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER],
) -> list[structs.OneMetaTag]:
    parsing_settings: typing.Final[typing.Mapping[str, str | tuple[str, ...]]] = structs.SETTINGS_FOR_SOCIAL_MEDIA[
        media_type
    ]
    output_buffer: typing.Final[list[structs.OneMetaTag]] = []
    for one_attr_group in all_tech_attrs:
        found_tag_name = _find_social_tag_name(one_attr_group, parsing_settings)
        if found_tag_name and "content" in one_attr_group and one_attr_group["content"].original:
            output_buffer.append(structs.OneMetaTag(name=found_tag_name, value=one_attr_group["content"].original))
    return output_buffer


def _extract_basic_tags_from_precursor(
    all_tech_attrs: list[dict[str, structs.ValuesGroup]],
) -> list[structs.OneMetaTag]:
    output_buffer: typing.Final[list[structs.OneMetaTag]] = []
    for one_attr_group in all_tech_attrs:
        tech_keys: KeysView[str] = one_attr_group.keys()

        if len(output_buffer) == len(structs.BASIC_META_TAGS):
            break
        output_buffer.extend(
            structs.OneMetaTag(
                name=one_ordinary_meta_tag,
                value=one_attr_group["content"].original,
            )
            for one_ordinary_meta_tag in structs.BASIC_META_TAGS
            if (
                "name" in tech_keys
                and one_attr_group["name"].normalized == one_ordinary_meta_tag
                and "content" in one_attr_group
                and one_attr_group["content"].original
            )
        )
    return output_buffer


def _match_social_prefix(one_attr_group: dict[str, structs.ValuesGroup], tech_keys: KeysView[str]) -> bool:
    return any(
        one_prop_name in tech_keys and one_attr_group[one_prop_name].normalized.startswith(one_config["prefix"])
        for one_config in structs.SETTINGS_FOR_SOCIAL_MEDIA.values()
        for one_prop_name in one_config["prop"]
    )


def _extract_all_other_tags_from_precursor(
    all_tech_attrs: list[dict[str, structs.ValuesGroup]],
) -> list[structs.OneMetaTag]:
    output_buffer: typing.Final[list[structs.OneMetaTag]] = []
    for one_attr_group in all_tech_attrs:
        tech_keys: KeysView[str] = one_attr_group.keys()
        if _match_social_prefix(one_attr_group, tech_keys):
            continue
        if "name" not in tech_keys or one_attr_group["name"].normalized in structs.BASIC_META_TAGS:
            continue
        if "content" in one_attr_group and one_attr_group["content"].original:
            output_buffer.append(
                structs.OneMetaTag(
                    name=one_attr_group["name"].normalized,
                    value=one_attr_group["content"].original,
                )
            )
    return output_buffer


def _prepare_normalized_meta_attrs(html_tree: LexborHTMLParser) -> list[dict[str, structs.ValuesGroup]]:
    normalized_meta_attrs: typing.Final[list[dict[str, structs.ValuesGroup]]] = []
    for one_meta_node in html_tree.css("meta"):
        prepared_attrs: dict[str, structs.ValuesGroup] = {}
        for attr_name, raw_value in one_meta_node.attributes.items():
            prepared_value: str = raw_value or ""
            prepared_attrs[attr_name.lower().strip()] = structs.ValuesGroup(
                original=prepared_value,
                normalized=prepared_value.lower().strip(),
            )
        normalized_meta_attrs.append(prepared_attrs)
    return normalized_meta_attrs


def parse_meta_tags_from_source(
    source_code: str | bytes,
    *,
    options: structs.SettingsFromUser | None = None,
) -> structs.TagsGroup:
    normalized_source: typing.Final[str] = (
        source_code.decode(errors="ignore") if isinstance(source_code, bytes) else source_code
    )
    active_options: typing.Final[structs.SettingsFromUser] = options or _GLOBAL_OPTIONS_HOLDER.get()
    html_tree: typing.Final[LexborHTMLParser] = LexborHTMLParser(
        _extract_html_scan_window(normalized_source, active_options)
        if active_options.optimize_input
        else normalized_source
    )
    title_node: typing.Final[LexborNode | None] = (
        html_tree.css_first("title") if structs.WhatToParse.TITLE in active_options.what_to_parse else None
    )
    page_title: typing.Final[str] = title_node.text().strip() if title_node else ""
    normalized_meta_attrs: typing.Final[list[dict[str, structs.ValuesGroup]]] = (
        _prepare_normalized_meta_attrs(html_tree)
        if any(
            one_item in active_options.what_to_parse
            for one_item in (
                structs.WhatToParse.OPEN_GRAPH,
                structs.WhatToParse.TWITTER,
                structs.WhatToParse.BASIC,
                structs.WhatToParse.OTHER,
            )
        )
        else []
    )

    open_graph_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_social_tags_from_precursor(normalized_meta_attrs, structs.WhatToParse.OPEN_GRAPH)
        if structs.WhatToParse.OPEN_GRAPH in active_options.what_to_parse
        else []
    )
    twitter_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_social_tags_from_precursor(normalized_meta_attrs, structs.WhatToParse.TWITTER)
        if structs.WhatToParse.TWITTER in active_options.what_to_parse
        else []
    )
    basic_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_basic_tags_from_precursor(normalized_meta_attrs)
        if structs.WhatToParse.BASIC in active_options.what_to_parse
        else []
    )
    other_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_all_other_tags_from_precursor(normalized_meta_attrs)
        if structs.WhatToParse.OTHER in active_options.what_to_parse
        else []
    )

    return structs.TagsGroup(
        title=page_title,
        basic=basic_meta_tags,
        open_graph=open_graph_meta_tags,
        twitter=twitter_meta_tags,
        other=other_meta_tags,
    )
