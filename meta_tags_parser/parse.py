import codecs
import contextvars
import functools
import re
import typing
from collections.abc import KeysView

from selectolax.lexbor import LexborHTMLParser, LexborNode

from . import structs


_GLOBAL_OPTIONS_HOLDER: typing.Final[contextvars.ContextVar[structs.SettingsFromUser]] = contextvars.ContextVar(
    "options", default=structs.DEFAULT_SETTINGS_FROM_USER
)
_CHARSET_DECLARATION_PATTERN: typing.Final = re.compile(rb"""charset\s*=\s*["']?([a-zA-Z0-9_.:+-]+)""", re.IGNORECASE)
BOUNDARY_PATTERN_CACHE_SIZE: typing.Final = 32
_CHARSET_LOOKUP_LIMIT: typing.Final = 4096
_BOM_CHARACTER: typing.Final = "\ufeff"
_BYTE_ORDER_MARKS: typing.Final[tuple[tuple[bytes, str], ...]] = (
    (codecs.BOM_UTF32_LE, "utf-32"),
    (codecs.BOM_UTF32_BE, "utf-32"),
    (codecs.BOM_UTF8, "utf-8-sig"),
    (codecs.BOM_UTF16_LE, "utf-16"),
    (codecs.BOM_UTF16_BE, "utf-16"),
)
_META_DEPENDENT_PARTS: typing.Final[frozenset[structs.WhatToParse]] = frozenset(
    (
        structs.WhatToParse.OPEN_GRAPH,
        structs.WhatToParse.TWITTER,
        structs.WhatToParse.BASIC,
        structs.WhatToParse.OTHER,
    )
)


def set_settings_for_meta_tags(new_options: structs.SettingsFromUser) -> None:
    """Override default package options."""
    _GLOBAL_OPTIONS_HOLDER.set(new_options)


def resolve_active_options(options: structs.SettingsFromUser | None) -> structs.SettingsFromUser:
    """Return explicit options or the ones installed by set_settings_for_meta_tags."""
    return options if options is not None else _GLOBAL_OPTIONS_HOLDER.get()


def _read_using_encoding(raw_source: bytes, encoding_name: str) -> str | None:
    # pages declare all kinds of nonsense: unknown names and non text codecs (charset="base64") raise
    # LookupError, and a few stdlib codecs (charset="idna") raise UnicodeError on arbitrary bytes
    try:
        return raw_source.decode(encoding_name, errors="ignore")
    except (LookupError, ValueError):
        return None


def convert_source_to_text(raw_source: bytes) -> str:
    """Decode raw page bytes honouring a byte order mark or a declared charset."""
    for one_byte_order_mark, one_bom_encoding in _BYTE_ORDER_MARKS:
        if raw_source.startswith(one_byte_order_mark):
            return raw_source.decode(one_bom_encoding, errors="ignore")
    found_charset: typing.Final[re.Match[bytes] | None] = _CHARSET_DECLARATION_PATTERN.search(
        raw_source[:_CHARSET_LOOKUP_LIMIT]
    )
    if found_charset is None:
        return raw_source.decode(errors="ignore")
    decoded_source: typing.Final[str | None] = _read_using_encoding(
        raw_source, found_charset.group(1).decode("ascii", errors="ignore")
    )
    if decoded_source is None:
        return raw_source.decode(errors="ignore")
    return decoded_source


@functools.lru_cache(maxsize=BOUNDARY_PATTERN_CACHE_SIZE)
def _build_boundary_pattern(boundary_tags: tuple[str, ...]) -> re.Pattern[str]:
    # only escaped literals end up in the alternation, so there is nothing here to backtrack on
    return re.compile("|".join(re.escape(one_boundary_tag) for one_boundary_tag in boundary_tags), re.IGNORECASE)


def _find_boundary_cut_position(found_boundary: re.Match[str], head_closing_tag: str) -> int:
    # the head closing tag is kept in the window, an opening body tag is not
    if found_boundary.group().lower() == head_closing_tag.lower():
        return found_boundary.end()
    return found_boundary.start()


def _extract_html_scan_window(html_source: str, active_options: structs.SettingsFromUser) -> str:
    # searching the original text (instead of a lowercased copy) keeps offsets valid: str.lower() is
    # not length preserving, U+0130 for example lowercases into two characters and shifts everything
    found_boundary: typing.Final[re.Match[str] | None] = (
        _build_boundary_pattern(tuple(active_options.boundary_tags)).search(
            html_source, 0, active_options.max_scan_chars
        )
        if active_options.boundary_tags
        else None
    )
    cut_position: typing.Final[int] = (
        _find_boundary_cut_position(found_boundary, active_options.boundary_tags[0])
        if found_boundary is not None
        else active_options.fallback_limit_chars
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
        one_attr_group[one_prop_name].normalized.removeprefix(tag_prefix)
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
    collected_basic_tags: typing.Final[dict[str, str]] = {}
    for one_attr_group in all_tech_attrs:
        tech_keys: KeysView[str] = one_attr_group.keys()
        if len(collected_basic_tags) == len(structs.BASIC_META_TAGS):
            break
        if "name" not in tech_keys or "content" not in tech_keys:
            continue
        basic_tag_name: str = one_attr_group["name"].normalized
        # duplicated basic tags are common in the wild, the first one wins and the rest are dropped
        if basic_tag_name not in structs.BASIC_META_TAGS or basic_tag_name in collected_basic_tags:
            continue
        if one_attr_group["content"].original:
            collected_basic_tags[basic_tag_name] = one_attr_group["content"].original
    return [
        structs.OneMetaTag(name=one_tag_name, value=one_tag_value)
        for one_tag_name, one_tag_value in collected_basic_tags.items()
    ]


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
        convert_source_to_text(source_code) if isinstance(source_code, bytes) else source_code.lstrip(_BOM_CHARACTER)
    )
    active_options: typing.Final[structs.SettingsFromUser] = resolve_active_options(options)
    requested_parts: typing.Final[frozenset[structs.WhatToParse]] = frozenset(active_options.what_to_parse)
    html_tree: typing.Final[LexborHTMLParser] = LexborHTMLParser(
        _extract_html_scan_window(normalized_source, active_options)
        if active_options.optimize_input
        else normalized_source
    )
    title_node: typing.Final[LexborNode | None] = (
        html_tree.css_first("title") if structs.WhatToParse.TITLE in requested_parts else None
    )
    page_title: typing.Final[str] = title_node.text().strip() if title_node else ""
    normalized_meta_attrs: typing.Final[list[dict[str, structs.ValuesGroup]]] = (
        _prepare_normalized_meta_attrs(html_tree) if requested_parts & _META_DEPENDENT_PARTS else []
    )

    open_graph_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_social_tags_from_precursor(normalized_meta_attrs, structs.WhatToParse.OPEN_GRAPH)
        if structs.WhatToParse.OPEN_GRAPH in requested_parts
        else []
    )
    twitter_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_social_tags_from_precursor(normalized_meta_attrs, structs.WhatToParse.TWITTER)
        if structs.WhatToParse.TWITTER in requested_parts
        else []
    )
    basic_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_basic_tags_from_precursor(normalized_meta_attrs)
        if structs.WhatToParse.BASIC in requested_parts
        else []
    )
    other_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_all_other_tags_from_precursor(normalized_meta_attrs)
        if structs.WhatToParse.OTHER in requested_parts
        else []
    )

    return structs.TagsGroup(
        title=page_title,
        basic=basic_meta_tags,
        open_graph=open_graph_meta_tags,
        twitter=twitter_meta_tags,
        other=other_meta_tags,
    )
