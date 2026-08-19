"""A deliberately naive reference implementation used as an independent oracle.

It is built on the standard library ``html.parser`` instead of selectolax, and it re-implements the
documented rules of this package from scratch: what counts as an Open Graph tag, a Twitter tag, a
basic tag and an "other" tag, and where the head ends. Real pages are then parsed twice, once by the
package and once by this module, and the two results must agree. A snapshot cannot catch a
regression that also updates the snapshot, two independent implementations can.
"""

import dataclasses
import html.parser
import typing


BASIC_META_TAG_NAMES: typing.Final[tuple[str, ...]] = ("title", "description", "keywords", "robots", "viewport")
HEAD_ENDING_TAGS: typing.Final[frozenset[str]] = frozenset(("head", "body"))


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class ReferenceResult:
    """What the reference implementation found inside the head of a page."""

    page_title: str
    open_graph_tags: list[list[str]]
    twitter_tags: list[list[str]]
    basic_tags: list[list[str]]
    other_tags: list[list[str]]


@typing.final
class ReferenceHeadParser(html.parser.HTMLParser):
    """Collect the title and every meta tag until the head is over."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.collected_meta: list[dict[str, str]] = []
        self.collected_title: str | None = None
        self.head_is_over: bool = False
        self.inside_title: bool = False

    def handle_starttag(self, tag_name: str, tag_attributes: list[tuple[str, str | None]]) -> None:
        if self.head_is_over:
            return
        if tag_name == "body":
            self.head_is_over = True
            return
        if tag_name == "title" and self.collected_title is None:
            self.inside_title = True
            self.collected_title = ""
            return
        if tag_name == "meta":
            self.collected_meta.append(
                {one_name.lower().strip(): (one_value or "") for one_name, one_value in tag_attributes}
            )

    def handle_endtag(self, tag_name: str) -> None:
        if tag_name in HEAD_ENDING_TAGS:
            self.head_is_over = True
        if tag_name == "title":
            self.inside_title = False

    def handle_data(self, data_text: str) -> None:
        if self.inside_title and self.collected_title is not None:
            self.collected_title += data_text


def _read_attribute(one_meta: dict[str, str], attribute_name: str) -> str:
    return one_meta.get(attribute_name, "").lower().strip()


def _collect_social_tags(
    collected_meta: list[dict[str, str]], tag_prefix: str, *, allowed_attributes: tuple[str, ...]
) -> list[list[str]]:
    collected_pairs: typing.Final[list[list[str]]] = []
    for one_meta in collected_meta:
        matching_names = [
            _read_attribute(one_meta, one_attribute).removeprefix(tag_prefix)
            for one_attribute in allowed_attributes
            if _read_attribute(one_meta, one_attribute).startswith(tag_prefix)
        ]
        if matching_names and one_meta.get("content"):
            collected_pairs.append([matching_names[0], one_meta["content"]])
    return collected_pairs


def _collect_basic_tags(collected_meta: list[dict[str, str]]) -> list[list[str]]:
    collected_values: typing.Final[dict[str, str]] = {}
    for one_meta in collected_meta:
        tag_name = _read_attribute(one_meta, "name")
        if "name" not in one_meta or tag_name not in BASIC_META_TAG_NAMES or not one_meta.get("content"):
            continue
        collected_values.setdefault(tag_name, one_meta["content"])
    return [[one_name, one_value] for one_name, one_value in collected_values.items()]


def _collect_other_tags(collected_meta: list[dict[str, str]]) -> list[list[str]]:
    return [
        [_read_attribute(one_meta, "name"), one_meta["content"]]
        for one_meta in collected_meta
        if "name" in one_meta
        and one_meta.get("content")
        and not _read_attribute(one_meta, "name").startswith("twitter:")
        and not _read_attribute(one_meta, "property").startswith(("twitter:", "og:"))
        and _read_attribute(one_meta, "name") not in BASIC_META_TAG_NAMES
    ]


def extract_reference_tags(page_text: str) -> ReferenceResult:
    """Parse the head of a page with the standard library and apply this package's documented rules."""
    reference_parser: typing.Final = ReferenceHeadParser()
    # the html specification normalizes newlines while preprocessing the input stream
    reference_parser.feed(page_text.replace("\r\n", "\n").replace("\r", "\n"))
    reference_parser.close()
    collected_meta: typing.Final[list[dict[str, str]]] = reference_parser.collected_meta
    return ReferenceResult(
        page_title=(reference_parser.collected_title or "").strip(),
        open_graph_tags=_collect_social_tags(collected_meta, "og:", allowed_attributes=("property",)),
        twitter_tags=_collect_social_tags(collected_meta, "twitter:", allowed_attributes=("name", "property")),
        basic_tags=_collect_basic_tags(collected_meta),
        other_tags=_collect_other_tags(collected_meta),
    )
