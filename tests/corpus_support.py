"""Access helpers for the corpus of pages captured from real sites.

The pages live in ``tests/html_corpus`` as gzipped copies of the exact bytes the site served, and
``pages.json`` records where each one came from. Everything is module level so that tests can
parametrize over the corpus at collection time.
"""

import dataclasses
import functools
import gzip
import json
import pathlib
import typing


CORPUS_DIRECTORY: typing.Final = pathlib.Path(__file__).parent / "html_corpus"
MANIFEST_PATH: typing.Final = CORPUS_DIRECTORY / "pages.json"


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class CorpusPageInfo:
    """One captured page: which site it came from and where the capture is stored."""

    page_slug: str
    file_name: str
    site_domain: str
    page_url: str
    language: str
    writing_system: str
    declared_charset: str
    raw_size_bytes: int
    captured_by: str

    def read_page_bytes(self) -> bytes:
        return gzip.decompress(CORPUS_DIRECTORY.joinpath(self.file_name).read_bytes())


@functools.lru_cache(maxsize=1)
def load_corpus_pages() -> tuple[CorpusPageInfo, ...]:
    manifest_data: typing.Final[typing.Mapping[str, typing.Any]] = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return tuple(
        CorpusPageInfo(
            page_slug=one_page["slug"],
            file_name=one_page["file_name"],
            site_domain=one_page["site"],
            page_url=one_page["page_url"],
            language=one_page["language"],
            writing_system=one_page["writing_system"],
            declared_charset=one_page["declared_charset"],
            raw_size_bytes=one_page["raw_size_bytes"],
            captured_by=one_page["captured_by"],
        )
        for one_page in manifest_data["pages"]
    )


ALL_CORPUS_PAGES: typing.Final[tuple[CorpusPageInfo, ...]] = load_corpus_pages()
CORPUS_PAGE_IDENTIFIERS: typing.Final[tuple[str, ...]] = tuple(one_page.page_slug for one_page in ALL_CORPUS_PAGES)


def convert_meta_tags_to_pairs(parsed_tags: typing.Iterable[typing.Any]) -> list[list[str]]:
    """Turn parsed OneMetaTag objects into the [name, value] pairs the reference parser returns."""
    return [[one_meta_tag.name, one_meta_tag.value] for one_meta_tag in parsed_tags]
