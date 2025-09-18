import typing

from meta_tags_parser import parse_meta_tags_from_source, set_settings_for_meta_tags, structs


def test_set_settings_for_meta_tags_overrides_defaults() -> None:
    html_text: typing.Final[str] = (
        "<html><head>"
        "<title>Site Title</title>"
        '<meta name="description" content="Example description">'
        '<meta property="og:title" content="OG Title">'
        '<meta name="twitter:title" content="Twitter Title">'
        "</head></html>"
    )
    restrictive_settings: typing.Final[structs.SettingsFromUser] = structs.SettingsFromUser(
        what_to_parse=(structs.WhatToParse.TITLE,),
    )
    set_settings_for_meta_tags(restrictive_settings)
    try:
        limited_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(html_text)
    finally:
        set_settings_for_meta_tags(structs.DEFAULT_SETTINGS_FROM_USER)

    assert limited_result.title == "Site Title"
    assert not limited_result.basic
    assert not limited_result.open_graph
    assert not limited_result.twitter
    assert not limited_result.other

    restored_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(html_text)
    assert restored_result.basic
    assert restored_result.open_graph
    assert restored_result.twitter
