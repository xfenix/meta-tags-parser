import contextvars
import typing

from selectolax.lexbor import LexborHTMLParser, LexborNode

from . import settings, structs


if typing.TYPE_CHECKING:
    from collections.abc import KeysView


_GLOBAL_OPTIONS_HOLDER: typing.Final[contextvars.ContextVar[structs.PackageOptions]] = contextvars.ContextVar("options")
_GLOBAL_OPTIONS_HOLDER.set(structs.PackageOptions())


def set_config_for_metatags(new_options: structs.PackageOptions) -> None:
    """Override default package options."""
    _GLOBAL_OPTIONS_HOLDER.set(new_options)


def _slice_html_for_meta(  # noqa: PLR0913
    html_source: str,
    *,
    optimize_input: bool = True,
    max_prefix_chars: int = 65536,
    max_scan_chars: int = 524288,
    hard_limit_chars: int | None = None,
    boundary_tags: tuple[str, str] = ("</head>", "<body"),
) -> str:
    if not optimize_input:
        return html_source
    scanning_prefix: str = html_source[:max_scan_chars]
    lowered_prefix: str = scanning_prefix.lower()
    earliest_position: int | None = None
    matched_boundary: str = ""
    for boundary_tag in boundary_tags:
        boundary_position: int = lowered_prefix.find(boundary_tag)
        if boundary_position != -1 and (earliest_position is None or boundary_position < earliest_position):
            earliest_position = boundary_position
            matched_boundary = boundary_tag
    if earliest_position is not None:
        cut_position: int = (
            earliest_position + len(boundary_tags[0]) if matched_boundary == boundary_tags[0] else earliest_position
        )
        limit_position: int = cut_position if hard_limit_chars is None else min(cut_position, hard_limit_chars)
        return html_source[:limit_position]
    return html_source[:max_prefix_chars]


def _extract_social_tags_from_precursor(
    all_tech_attrs: list[dict[str, structs.ValuesGroup]],
    media_type: typing.Literal[structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER],
) -> list[structs.OneMetaTag]:
    possible_settings_for_parsing: typing.Final[typing.Mapping[str, str | tuple[str, ...]]] = (
        settings.SETTINGS_FOR_SOCIAL_MEDIA[media_type]
    )
    output_buffer: typing.Final[list[structs.OneMetaTag]] = []
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
    all_tech_attrs: list[dict[str, structs.ValuesGroup]],
) -> list[structs.OneMetaTag]:
    output_buffer: typing.Final[list[structs.OneMetaTag]] = []
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
    all_tech_attrs: list[dict[str, structs.ValuesGroup]],
) -> list[structs.OneMetaTag]:
    output_buffer: typing.Final[list[structs.OneMetaTag]] = []
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
    html_tree: LexborHTMLParser,
) -> list[dict[str, structs.ValuesGroup]]:
    normalized_meta_attrs: typing.Final[list[dict[str, structs.ValuesGroup]]] = []
    for meta_node in html_tree.css("meta"):
        prepared_attrs: dict[str, structs.ValuesGroup] = {}
        for attr_name, raw_value in meta_node.attributes.items():
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
    options: structs.PackageOptions | None = None,
) -> structs.TagsGroup:
    """Parse meta tags from source code."""
    if isinstance(source_code, bytes):
        normalized_source: str = source_code.decode(errors="ignore")
    else:
        normalized_source = source_code

    active_options: structs.PackageOptions = options or _GLOBAL_OPTIONS_HOLDER.get()
    sliced_source: str = _slice_html_for_meta(
        normalized_source,
        optimize_input=active_options.optimize_input,
        max_prefix_chars=active_options.max_prefix_chars,
        max_scan_chars=active_options.max_scan_chars,
        hard_limit_chars=active_options.hard_limit_chars,
        boundary_tags=active_options.boundary_tags,
    )

    what_to_parse: tuple[structs.WhatToParse, ...] = active_options.what_to_parse

    html_tree: typing.Final[LexborHTMLParser] = LexborHTMLParser(sliced_source)
    title_node: typing.Final[LexborNode | None] = (
        html_tree.css_first("title") if structs.WhatToParse.TITLE in what_to_parse else None
    )
    page_title: typing.Final[str] = title_node.text().strip() if title_node else ""

    should_parse_meta: typing.Final[bool] = any(
        one in what_to_parse
        for one in (
            structs.WhatToParse.OPEN_GRAPH,
            structs.WhatToParse.TWITTER,
            structs.WhatToParse.BASIC,
            structs.WhatToParse.OTHER,
        )
    )

    normalized_meta_attrs: typing.Final[list[dict[str, structs.ValuesGroup]]] = (
        _prepare_normalized_meta_attrs(html_tree) if should_parse_meta else []
    )

    open_graph_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_social_tags_from_precursor(normalized_meta_attrs, structs.WhatToParse.OPEN_GRAPH)
        if structs.WhatToParse.OPEN_GRAPH in what_to_parse
        else []
    )

    twitter_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_social_tags_from_precursor(normalized_meta_attrs, structs.WhatToParse.TWITTER)
        if structs.WhatToParse.TWITTER in what_to_parse
        else []
    )

    basic_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_basic_tags_from_precursor(normalized_meta_attrs) if structs.WhatToParse.BASIC in what_to_parse else []
    )

    other_meta_tags: typing.Final[list[structs.OneMetaTag]] = (
        _extract_all_other_tags_from_precursor(normalized_meta_attrs)
        if structs.WhatToParse.OTHER in what_to_parse
        else []
    )

    return structs.TagsGroup(
        title=page_title,
        basic=basic_meta_tags,
        open_graph=open_graph_meta_tags,
        twitter=twitter_meta_tags,
        other=other_meta_tags,
    )
