"""Parse pages captured from real sites, with expectations taken from the stored markup."""

import pathlib
import typing

import pytest

from meta_tags_parser import parse_meta_tags_from_source, parse_snippets_from_source, structs
from tests import conftest


@typing.final
class CapturedPageExpectation(typing.NamedTuple):
    """What a captured page must produce."""

    file_stem: str
    page_title: str
    open_graph_title: str
    open_graph_url: str
    twitter_card: str
    basic_tag_names: frozenset[str]
    other_tags_count: int


CAPTURED_PAGE_EXPECTATIONS: typing.Final[tuple[CapturedPageExpectation, ...]] = (
    CapturedPageExpectation(
        file_stem="chatgpt-com",
        page_title="ChatGPT",
        open_graph_title="ChatGPT",
        open_graph_url="https://chatgpt.com/?locale=en-US",
        twitter_card="",
        basic_tag_names=frozenset(("viewport", "description", "robots")),
        other_tags_count=4,
    ),
    CapturedPageExpectation(
        file_stem="gazeta-ru",
        page_title="В\xa0ВОЗ предупредили о\xa0«цунами» новых случаев COVID-19 - Газета.Ru | Новости",
        open_graph_title="В\xa0ВОЗ предупредили о\xa0«цунами» новых случаев COVID-19 - Газета.Ru | Новости",
        open_graph_url="https://www.gazeta.ru/social/news/2021/12/29/17083219.shtml",
        twitter_card="summary_large_image",
        basic_tag_names=frozenset(("viewport", "robots", "description", "keywords")),
        other_tags_count=0,
    ),
    CapturedPageExpectation(
        file_stem="github-com",
        page_title="GitHub",
        open_graph_title="Build software better, together",
        open_graph_url="https://github.com",
        twitter_card="summary_large_image",
        basic_tag_names=frozenset(("viewport", "description")),
        other_tags_count=32,
    ),
    CapturedPageExpectation(
        file_stem="globo-com",
        page_title=(
            "Demanda por testes de Covid em farmácias aumenta 44% em duas semanas no Brasil, "
            "diz associação | Coronavírus | G1"
        ),
        open_graph_title=(
            "Demanda por testes de Covid em farmácias aumenta 44% em duas semanas no Brasil, diz associação"
        ),
        open_graph_url=(
            "https://g1.globo.com/saude/coronavirus/noticia/2021/12/29/"
            "testes-de-covid-em-farmacias-aumenta-44percent-em-duas-semanas-no-brasil-diz-associacao.ghtml"
        ),
        twitter_card="summary_large_image",
        basic_tag_names=frozenset(("viewport", "title", "description", "robots")),
        other_tags_count=0,
    ),
)


def _read_captured_page(file_stem: str) -> bytes:
    return conftest.FIXTURES_DIRECTORY.joinpath(f"{file_stem}.html").read_bytes()


def _find_tag_value(parsed_tags: list[structs.OneMetaTag], tag_name: str) -> str:
    matching_values: typing.Final[list[str]] = [
        one_meta_tag.value for one_meta_tag in parsed_tags if one_meta_tag.name == tag_name
    ]
    return matching_values[0] if matching_values else ""


@pytest.mark.parametrize(
    "one_expectation",
    CAPTURED_PAGE_EXPECTATIONS,
    ids=[one_expectation.file_stem for one_expectation in CAPTURED_PAGE_EXPECTATIONS],
)
def test_captured_page_is_parsed_as_expected(one_expectation: CapturedPageExpectation) -> None:
    parse_result: typing.Final[structs.TagsGroup] = parse_meta_tags_from_source(
        _read_captured_page(one_expectation.file_stem)
    )

    assert parse_result.title == one_expectation.page_title
    assert _find_tag_value(parse_result.open_graph, "title") == one_expectation.open_graph_title
    assert _find_tag_value(parse_result.open_graph, "url") == one_expectation.open_graph_url
    assert _find_tag_value(parse_result.twitter, "card") == one_expectation.twitter_card
    assert {one_meta_tag.name for one_meta_tag in parse_result.basic} == one_expectation.basic_tag_names
    assert len(parse_result.other) == one_expectation.other_tags_count


@pytest.mark.parametrize(
    "one_expectation",
    CAPTURED_PAGE_EXPECTATIONS,
    ids=[one_expectation.file_stem for one_expectation in CAPTURED_PAGE_EXPECTATIONS],
)
def test_captured_page_snippet(one_expectation: CapturedPageExpectation) -> None:
    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(
        _read_captured_page(one_expectation.file_stem)
    )

    assert snippet_result.open_graph.title == one_expectation.open_graph_title
    assert snippet_result.open_graph.url == one_expectation.open_graph_url
    assert snippet_result.open_graph.image.startswith("http")
    assert snippet_result.open_graph.image_width >= 0


def test_all_captured_pages_are_covered(provide_html_file_paths: list[pathlib.Path]) -> None:
    assert {one_path.stem for one_path in provide_html_file_paths} == {
        one_expectation.file_stem for one_expectation in CAPTURED_PAGE_EXPECTATIONS
    }
