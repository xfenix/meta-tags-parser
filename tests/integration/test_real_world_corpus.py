"""Parse the whole generated corpus of real world shaped pages.

Every page carries the tags it was built from (``tests/html_corpus/expectations.json``), so these
tests compare against what was written into the markup, not against a snapshot of parser output.
"""

import typing

import pytest

from meta_tags_parser import parse_meta_tags_from_source, parse_snippets_from_source, structs
from tests import corpus_support


LARGE_PAGE_THRESHOLD_BYTES: typing.Final = 100_000
EXPECTED_CORPUS_SIZE: typing.Final = 100
EXPECTED_LANGUAGES_COUNT: typing.Final = 15
EXPECTED_ARCHETYPES_COUNT: typing.Final = 10
EXPECTED_QUIRKS_COUNT: typing.Final = 20
EXPECTED_ENCODINGS_COUNT: typing.Final = 5
EXPECTED_LARGE_PAGES_COUNT: typing.Final = 10
FULL_SCAN_SETTINGS: typing.Final = structs.SettingsFromUser(optimize_input=False)


def _assert_matches_expectations(
    parse_result: structs.TagsGroup,
    snippet_result: structs.SnippetGroup,
    *,
    expected_group: typing.Mapping[str, typing.Any],
) -> None:
    assert parse_result.title == expected_group["title"]
    assert corpus_support.convert_meta_tags_to_pairs(parse_result.basic) == expected_group["basic"]
    assert corpus_support.convert_meta_tags_to_pairs(parse_result.open_graph) == expected_group["open_graph"]
    assert corpus_support.convert_meta_tags_to_pairs(parse_result.twitter) == expected_group["twitter"]
    assert corpus_support.convert_meta_tags_to_pairs(parse_result.other) == expected_group["other"]
    assert snippet_result.open_graph == structs.SocialMediaSnippet(**expected_group["snippet_open_graph"])
    assert snippet_result.twitter == structs.SocialMediaSnippet(**expected_group["snippet_twitter"])


@pytest.mark.parametrize("one_corpus_page", corpus_support.ALL_CORPUS_PAGES, ids=corpus_support.CORPUS_PAGE_IDENTIFIERS)
def test_corpus_page_with_default_settings(one_corpus_page: corpus_support.CorpusPageInfo) -> None:
    page_bytes: typing.Final[bytes] = one_corpus_page.read_page_bytes()

    _assert_matches_expectations(
        parse_meta_tags_from_source(page_bytes),
        parse_snippets_from_source(page_bytes),
        expected_group=one_corpus_page.expected_default,
    )


@pytest.mark.parametrize("one_corpus_page", corpus_support.ALL_CORPUS_PAGES, ids=corpus_support.CORPUS_PAGE_IDENTIFIERS)
def test_corpus_page_without_input_optimization(one_corpus_page: corpus_support.CorpusPageInfo) -> None:
    page_bytes: typing.Final[bytes] = one_corpus_page.read_page_bytes()

    _assert_matches_expectations(
        parse_meta_tags_from_source(page_bytes, options=FULL_SCAN_SETTINGS),
        parse_snippets_from_source(page_bytes, options=FULL_SCAN_SETTINGS),
        expected_group=one_corpus_page.expected_full,
    )


@pytest.mark.parametrize("one_corpus_page", corpus_support.ALL_CORPUS_PAGES, ids=corpus_support.CORPUS_PAGE_IDENTIFIERS)
def test_corpus_page_invariants(one_corpus_page: corpus_support.CorpusPageInfo) -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(one_corpus_page.read_page_bytes())

    assert parse_result.title == parse_result.title.strip()
    for one_meta_tag in (*parse_result.basic, *parse_result.open_graph, *parse_result.twitter, *parse_result.other):
        assert one_meta_tag.value, "tags without content must never be returned"
        assert one_meta_tag.name == one_meta_tag.name.lower().strip(), "tag names are normalized"
    for one_social_tag in (*parse_result.open_graph, *parse_result.twitter):
        assert not one_social_tag.name.startswith(("og:", "twitter:")), "social prefixes are stripped"
    assert len({one_meta_tag.name for one_meta_tag in parse_result.basic}) == len(parse_result.basic)
    assert {one_meta_tag.name for one_meta_tag in parse_result.basic} <= set(structs.BASIC_META_TAGS)


def test_corpus_covers_the_interesting_shapes() -> None:
    all_pages: typing.Final[tuple[corpus_support.CorpusPageInfo, ...]] = corpus_support.ALL_CORPUS_PAGES
    large_pages: typing.Final[list[corpus_support.CorpusPageInfo]] = [
        one_page for one_page in all_pages if one_page.raw_size_bytes > LARGE_PAGE_THRESHOLD_BYTES
    ]

    assert len(all_pages) == EXPECTED_CORPUS_SIZE
    assert len({one_page.language for one_page in all_pages}) >= EXPECTED_LANGUAGES_COUNT
    assert len({one_page.archetype for one_page in all_pages}) >= EXPECTED_ARCHETYPES_COUNT
    assert len({one_page.quirk_name for one_page in all_pages}) >= EXPECTED_QUIRKS_COUNT
    assert len({one_page.encoding for one_page in all_pages}) >= EXPECTED_ENCODINGS_COUNT
    assert len(large_pages) >= EXPECTED_LARGE_PAGES_COUNT
