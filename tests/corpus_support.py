"""Access helpers for the generated real-world HTML corpus.

The corpus itself is built by ``scripts/generate_html_corpus.py``; here we only read the manifest and
unpack pages on demand. Everything is module level so that tests can parametrize over the corpus at
collection time.
"""

import dataclasses
import functools
import gzip
import json
import pathlib
import typing


CORPUS_DIRECTORY: typing.Final = pathlib.Path(__file__).parent / "html_corpus"
EXPECTATIONS_PATH: typing.Final = CORPUS_DIRECTORY / "expectations.json"


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class CorpusPageInfo:
    """One corpus page: where it lives and what the parser is expected to return for it."""

    page_slug: str
    file_name: str
    language: str
    archetype: str
    quirk_name: str
    encoding: str
    raw_size_bytes: int
    expected_default: typing.Mapping[str, typing.Any]
    expected_full: typing.Mapping[str, typing.Any]

    def read_page_bytes(self) -> bytes:
        return gzip.decompress(CORPUS_DIRECTORY.joinpath(self.file_name).read_bytes())


@functools.lru_cache(maxsize=1)
def load_corpus_pages() -> tuple[CorpusPageInfo, ...]:
    manifest_data: typing.Final[typing.Mapping[str, typing.Any]] = json.loads(
        EXPECTATIONS_PATH.read_text(encoding="utf-8")
    )
    return tuple(
        CorpusPageInfo(
            page_slug=one_page["slug"],
            file_name=one_page["file_name"],
            language=one_page["language"],
            archetype=one_page["archetype"],
            quirk_name=one_page["quirk"],
            encoding=one_page["encoding"],
            raw_size_bytes=one_page["raw_size_bytes"],
            expected_default=one_page["expected_default"],
            expected_full=one_page["expected_full"],
        )
        for one_page in manifest_data["pages"]
    )


ALL_CORPUS_PAGES: typing.Final[tuple[CorpusPageInfo, ...]] = load_corpus_pages()
CORPUS_PAGE_IDENTIFIERS: typing.Final[tuple[str, ...]] = tuple(one_page.page_slug for one_page in ALL_CORPUS_PAGES)


def convert_meta_tags_to_pairs(parsed_tags: typing.Iterable[typing.Any]) -> list[list[str]]:
    """Turn parsed OneMetaTag objects into the [name, value] pairs the manifest stores."""
    return [[one_meta_tag.name, one_meta_tag.value] for one_meta_tag in parsed_tags]
