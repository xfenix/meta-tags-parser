import dataclasses
import typing

import pytest

from meta_tags_parser import parse_meta_tags_from_source, parse_snippets_from_source, structs
from tests import conftest


MULTILINE_PAGE_FIXTURE: typing.Final = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <!-- Open Graph / Facebook -->
    <meta name="single-tag-without-content">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://metatags.io/">
    <meta property="og:title" content="Meta Tags — Preview, Edit and Generate">
    <meta property="og:description" content="With Meta Tags you can edit and
    experiment with your content then preview how your webpage will look on Google, Facebook, Twitter and more!">
    <meta property="og:image"
    content="https://metatags.io/assets/meta-tags-16a33a6a8531e519cc0936fbba0ad904e52d35f34a46c97a2c9f6f7dd7d336f2.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://metatags.io/">
    <meta property="twitter:title" content="Privet, kak dela to vcelom?">
    <meta property="twitter:image" content="https://metatags.io/assets/hm-fail.png">
</head>
<body>
    <a href="#">Kek</a>
</body>
</html>
"""
EXPECTED_TWITTER_TAGS_COUNT: typing.Final = 4
BASIC_TAGS_LIMIT: typing.Final = 5


def test_parse_title_and_social_tags_from_static_page() -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(MULTILINE_PAGE_FIXTURE)

    assert parse_result.title == "Document"
    assert parse_result.open_graph == [
        structs.OneMetaTag(name="type", value="website"),
        structs.OneMetaTag(name="url", value="https://metatags.io/"),
        structs.OneMetaTag(name="title", value="Meta Tags — Preview, Edit and Generate"),
        structs.OneMetaTag(
            name="description",
            value=(
                "With Meta Tags you can edit and\n"
                "    experiment with your content then preview how your webpage will look on Google, "
                "Facebook, Twitter and more!"
            ),
        ),
        structs.OneMetaTag(
            name="image",
            value=(
                "https://metatags.io/assets/meta-tags-16a33a6a8531e5"
                "19cc0936fbba0ad904e52d35f34a46c97a2c9f6f7dd7d336f2.png"
            ),
        ),
        structs.OneMetaTag(name="image:width", value="1200"),
        structs.OneMetaTag(name="image:height", value="630"),
    ]
    assert parse_result.twitter == [
        structs.OneMetaTag(name="card", value="summary_large_image"),
        structs.OneMetaTag(name="url", value="https://metatags.io/"),
        structs.OneMetaTag(name="title", value="Privet, kak dela to vcelom?"),
        structs.OneMetaTag(name="image", value="https://metatags.io/assets/hm-fail.png"),
    ]
    assert parse_result.basic == [structs.OneMetaTag(name="viewport", value="width=device-width, initial-scale=1.0")]
    assert parse_result.other == []


@pytest.mark.parametrize("social_attribute_name", ["name", "property"])
def test_twitter_tags_are_read_from_both_attributes(social_attribute_name: str) -> None:
    page_fixture: typing.Final[str] = "\n".join(
        f'<meta {social_attribute_name}="twitter:{one_tag_name}" content="value of {one_tag_name}">'
        for one_tag_name in ("card", "url", "title", "description")
    )

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_fixture)

    assert len(parse_result.twitter) == EXPECTED_TWITTER_TAGS_COUNT


def test_open_graph_tags_are_read_only_from_the_property_attribute() -> None:
    """Open Graph is specified on `property`, a `name` based tag stays an ordinary other tag."""
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        '<meta name="og:title" content="named og">'
    )

    assert parse_result.open_graph == []
    assert parse_result.other == [structs.OneMetaTag(name="og:title", value="named og")]


def test_duplicated_basic_tags_keep_the_first_value_and_do_not_hide_the_rest() -> None:
    """Five repeated descriptions used to fill the basic tag budget and drop everything after them."""
    page_fixture: typing.Final[str] = (
        "".join(f'<meta name="description" content="description {one_number}">' for one_number in range(5))
        + '<meta name="keywords" content="one, two">'
        + '<meta name="robots" content="index">'
    )

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_fixture)

    assert parse_result.basic == [
        structs.OneMetaTag(name="description", value="description 0"),
        structs.OneMetaTag(name="keywords", value="one, two"),
        structs.OneMetaTag(name="robots", value="index"),
    ]


def test_basic_tags_never_exceed_the_known_tag_names() -> None:
    page_fixture: typing.Final[str] = "".join(
        f'<meta name="{one_tag_name}" content="value">' for one_tag_name in structs.BASIC_META_TAGS
    )

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_fixture)

    assert len(parse_result.basic) == BASIC_TAGS_LIMIT
    assert {one_meta_tag.name for one_meta_tag in parse_result.basic} == set(structs.BASIC_META_TAGS)


@pytest.mark.parametrize(
    "page_fixture",
    [
        '<meta property="og:title" content="">',
        '<meta property="og:title">',
        '<meta name="twitter:title" content="">',
        '<meta name="description" content="">',
        '<meta name="custom-tag" content="">',
        "<meta>",
    ],
)
def test_tags_without_content_are_skipped(page_fixture: str) -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_fixture)

    assert parse_result == structs.TagsGroup(title="")


def test_upper_case_markup_is_normalized() -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        '<META PROPERTY="OG:TITLE" CONTENT="Upper Case Value">'
    )

    assert parse_result.open_graph == [structs.OneMetaTag(name="title", value="Upper Case Value")]


def test_html_entities_are_decoded() -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        '<title>Caf&eacute; &amp; Bar</title><meta name="description" content="&lt;b&gt;bold&lt;/b&gt; &#1055;">'
    )

    assert parse_result.title == "Café & Bar"
    assert parse_result.basic == [structs.OneMetaTag(name="description", value="<b>bold</b> П")]


def test_results_handed_to_the_user_are_immutable() -> None:
    """Every struct the public API returns is frozen, callers may cache a result without copying it."""
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(MULTILINE_PAGE_FIXTURE)
    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(MULTILINE_PAGE_FIXTURE)
    frozen_instances: typing.Final[tuple[object, ...]] = (
        parse_result,
        parse_result.open_graph[0],
        snippet_result,
        snippet_result.open_graph,
    )

    for one_instance, one_field_name in zip(frozen_instances, ("title", "name", "twitter", "title"), strict=True):
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(one_instance, one_field_name, "mutated")


def test_tags_after_the_head_are_ignored_by_default() -> None:
    page_fixture: typing.Final = (
        '<html><head><title>Head title</title></head><body><meta property="og:title" content="late"></body></html>'
    )

    assert parse_meta_tags_from_source(page_fixture).open_graph == []
    assert parse_meta_tags_from_source(
        page_fixture, options=structs.SettingsFromUser(optimize_input=False)
    ).open_graph == [structs.OneMetaTag(name="title", value="late")]


def test_parse_from_generated_page(provide_fake_meta_page: conftest.FakeMetaPage) -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(provide_fake_meta_page.html_source)

    for one_group in (parse_result.open_graph, parse_result.twitter):
        for one_meta_tag in one_group:
            assert one_meta_tag.name in provide_fake_meta_page.social_tag_values
    assert parse_result.title
    assert [one_meta_tag.name for one_meta_tag in parse_result.other] == list(provide_fake_meta_page.other_tag_names)


def test_only_the_leading_social_prefix_is_stripped() -> None:
    """A repeated prefix inside the tag name must survive, only the leading one is removed."""
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        '<meta property="og:see_also:og:url" content="https://example.com/">'
    )

    assert parse_result.open_graph == [structs.OneMetaTag(name="see_also:og:url", value="https://example.com/")]
