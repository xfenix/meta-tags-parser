"""Parse a hundred pages captured from real sites, in the encodings those sites served them in.

Nothing here is a snapshot of parser output: every expectation comes from ``tests/reference_parser``,
an independent implementation of the same documented rules built on the standard library instead of
selectolax. If the two disagree on a real page, one of them has a bug.
"""

import types
import typing

import pytest

from meta_tags_parser import parse_meta_tags_from_source, parse_snippets_from_source, structs
from meta_tags_parser.parse import convert_source_to_text
from tests import corpus_support, reference_parser


FULL_SCAN_SETTINGS: typing.Final = structs.SettingsFromUser(optimize_input=False)
LARGE_PAGE_THRESHOLD_BYTES: typing.Final = 100_000
EXPECTED_CORPUS_SIZE: typing.Final = 100
EXPECTED_SITES_COUNT: typing.Final = 90
EXPECTED_LANGUAGES_COUNT: typing.Final = 25
EXPECTED_WRITING_SYSTEMS_COUNT: typing.Final = 10
EXPECTED_LEGACY_ENCODED_COUNT: typing.Final = 5
EXPECTED_LARGE_PAGES_COUNT: typing.Final = 40
LEGACY_ENCODING_NAMES: typing.Final[frozenset[str]] = frozenset(
    ("iso-8859-1", "iso-8859-2", "iso-8859-15", "windows-1250", "windows-1251", "windows-1252", "euc-kr", "gb2312")
)
DOCUMENTED_RULES_PAGE_FIXTURE: typing.Final = (
    "<html><head>"
    "<title>  padded &amp; escaped  </title>"
    '<meta property="og:title" content="og value">'
    '<meta property="og:description" content="first\r\nsecond">'
    '<meta name="twitter:card" content="summary">'
    '<meta property="twitter:title" content="twitter via property">'
    '<meta name="description" content="first description">'
    '<meta name="description" content="second description">'
    '<meta name="generator" content="hand made">'
    '<meta name="og:audio" content="og via name">'
    '<meta name="image" property="og:image" content="both attributes">'
    '<meta name="empty" content="">'
    "</head>"
    '<meta property="og:title" content="after the head">'
    '<body><meta property="og:title" content="inside the body">'
)
UNCLOSED_HEAD_PAGE_FIXTURE: typing.Final = (
    "<html><head><title>Head title</title>"
    '<meta property="og:title" content="in the head">'
    '<body><meta property="og:title" content="in the body">'
)
EXPECTED_DOCUMENTED_TITLE: typing.Final = "padded & escaped"
EXPECTED_DOCUMENTED_TAGS: typing.Final[typing.Mapping[str, list[list[str]]]] = types.MappingProxyType(
    {
        "open_graph": [["title", "og value"], ["description", "first\nsecond"], ["image", "both attributes"]],
        "twitter": [["card", "summary"], ["title", "twitter via property"]],
        "basic": [["description", "first description"]],
        "other": [["generator", "hand made"], ["og:audio", "og via name"]],
    }
)


def test_package_and_reference_agree_on_the_documented_rules() -> None:
    """The oracle is only worth its name while it independently reproduces the rules on a known page."""
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(DOCUMENTED_RULES_PAGE_FIXTURE)
    reference_result: typing.Final[reference_parser.ReferenceResult] = reference_parser.extract_reference_tags(
        DOCUMENTED_RULES_PAGE_FIXTURE
    )

    assert parse_result.title == EXPECTED_DOCUMENTED_TITLE
    assert reference_result.page_title == EXPECTED_DOCUMENTED_TITLE
    for one_field_name, expected_pairs in EXPECTED_DOCUMENTED_TAGS.items():
        assert corpus_support.convert_meta_tags_to_pairs(getattr(parse_result, one_field_name)) == expected_pairs
        assert getattr(reference_result, f"{one_field_name}_tags") == expected_pairs


def test_package_and_reference_stop_at_the_body_start_tag() -> None:
    """Plenty of pages never close their head, both implementations then stop at the opening body tag."""
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(UNCLOSED_HEAD_PAGE_FIXTURE)
    reference_result: typing.Final[reference_parser.ReferenceResult] = reference_parser.extract_reference_tags(
        UNCLOSED_HEAD_PAGE_FIXTURE
    )

    assert parse_result.title == reference_result.page_title == "Head title"
    assert corpus_support.convert_meta_tags_to_pairs(parse_result.open_graph) == [["title", "in the head"]]
    assert reference_result.open_graph_tags == [["title", "in the head"]]


@pytest.mark.parametrize("one_corpus_page", corpus_support.ALL_CORPUS_PAGES, ids=corpus_support.CORPUS_PAGE_IDENTIFIERS)
def test_real_page_matches_the_reference_parser(one_corpus_page: corpus_support.CorpusPageInfo) -> None:
    page_bytes: typing.Final[bytes] = one_corpus_page.read_page_bytes()
    expected_result: typing.Final[reference_parser.ReferenceResult] = reference_parser.extract_reference_tags(
        convert_source_to_text(page_bytes)
    )

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_bytes)

    assert parse_result.title == expected_result.page_title
    assert corpus_support.convert_meta_tags_to_pairs(parse_result.open_graph) == expected_result.open_graph_tags
    assert corpus_support.convert_meta_tags_to_pairs(parse_result.twitter) == expected_result.twitter_tags
    assert corpus_support.convert_meta_tags_to_pairs(parse_result.basic) == expected_result.basic_tags
    assert corpus_support.convert_meta_tags_to_pairs(parse_result.other) == expected_result.other_tags


@pytest.mark.parametrize("one_corpus_page", corpus_support.ALL_CORPUS_PAGES, ids=corpus_support.CORPUS_PAGE_IDENTIFIERS)
def test_full_scan_starts_with_the_head_tags(one_corpus_page: corpus_support.CorpusPageInfo) -> None:
    """Scanning the whole document may add tags placed in the body, never reorder or drop head ones."""
    page_bytes: typing.Final[bytes] = one_corpus_page.read_page_bytes()
    expected_result: typing.Final[reference_parser.ReferenceResult] = reference_parser.extract_reference_tags(
        convert_source_to_text(page_bytes)
    )

    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(page_bytes, options=FULL_SCAN_SETTINGS)

    for parsed_group, expected_group in (
        (parse_result.open_graph, expected_result.open_graph_tags),
        (parse_result.twitter, expected_result.twitter_tags),
        (parse_result.other, expected_result.other_tags),
    ):
        assert corpus_support.convert_meta_tags_to_pairs(parsed_group)[: len(expected_group)] == expected_group


@pytest.mark.parametrize("one_corpus_page", corpus_support.ALL_CORPUS_PAGES, ids=corpus_support.CORPUS_PAGE_IDENTIFIERS)
def test_real_page_snippets_take_the_first_value(one_corpus_page: corpus_support.CorpusPageInfo) -> None:
    page_bytes: typing.Final[bytes] = one_corpus_page.read_page_bytes()
    expected_result: typing.Final[reference_parser.ReferenceResult] = reference_parser.extract_reference_tags(
        convert_source_to_text(page_bytes)
    )

    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(page_bytes)

    for expected_pairs, one_snippet in (
        (expected_result.open_graph_tags, snippet_result.open_graph),
        (expected_result.twitter_tags, snippet_result.twitter),
    ):
        for one_field_name in ("title", "description", "image", "url"):
            first_values = [
                one_value for one_name, one_value in expected_pairs if one_name.replace(":", "_") == one_field_name
            ]
            assert getattr(one_snippet, one_field_name) == (first_values[0] if first_values else "")


@pytest.mark.parametrize("one_corpus_page", corpus_support.ALL_CORPUS_PAGES, ids=corpus_support.CORPUS_PAGE_IDENTIFIERS)
def test_real_page_invariants(one_corpus_page: corpus_support.CorpusPageInfo) -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(one_corpus_page.read_page_bytes())

    assert parse_result.title == parse_result.title.strip()
    for one_meta_tag in (*parse_result.basic, *parse_result.open_graph, *parse_result.twitter, *parse_result.other):
        assert one_meta_tag.value, "tags without content must never be returned"
        assert one_meta_tag.name == one_meta_tag.name.lower().strip(), "tag names are normalized"
    for one_social_tag in (*parse_result.open_graph, *parse_result.twitter):
        assert not one_social_tag.name.startswith(("og:", "twitter:")), "social prefixes are stripped"
    assert len({one_meta_tag.name for one_meta_tag in parse_result.basic}) == len(parse_result.basic)
    assert {one_meta_tag.name for one_meta_tag in parse_result.basic} <= set(structs.BASIC_META_TAGS)


def test_corpus_covers_many_sites_languages_and_encodings() -> None:
    all_pages: typing.Final[tuple[corpus_support.CorpusPageInfo, ...]] = corpus_support.ALL_CORPUS_PAGES
    legacy_encoded_pages: typing.Final[list[corpus_support.CorpusPageInfo]] = [
        one_page for one_page in all_pages if one_page.declared_charset in LEGACY_ENCODING_NAMES
    ]
    large_pages: typing.Final[list[corpus_support.CorpusPageInfo]] = [
        one_page for one_page in all_pages if one_page.raw_size_bytes > LARGE_PAGE_THRESHOLD_BYTES
    ]

    assert len(all_pages) == EXPECTED_CORPUS_SIZE
    assert len({one_page.site_domain for one_page in all_pages}) >= EXPECTED_SITES_COUNT
    assert len({one_page.language for one_page in all_pages if one_page.language}) >= EXPECTED_LANGUAGES_COUNT
    assert len({one_page.writing_system for one_page in all_pages}) >= EXPECTED_WRITING_SYSTEMS_COUNT
    assert len(legacy_encoded_pages) >= EXPECTED_LEGACY_ENCODED_COUNT
    assert len(large_pages) >= EXPECTED_LARGE_PAGES_COUNT


def test_every_corpus_page_records_its_origin() -> None:
    stored_files: typing.Final[set[str]] = {
        one_path.name for one_path in corpus_support.CORPUS_DIRECTORY.glob("*.html.gz")
    }

    assert stored_files == {one_page.file_name for one_page in corpus_support.ALL_CORPUS_PAGES}
    for one_page in corpus_support.ALL_CORPUS_PAGES:
        assert one_page.site_domain, "every page must name the site it was captured from"
        assert one_page.page_url.startswith("http"), "every page must record its original address"
        assert one_page.captured_by, "every page must name the corpus it was taken from"
