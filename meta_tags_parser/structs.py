import dataclasses
import enum
import functools
import typing


@functools.cache
def _normalize_tag_name(tag_name: str) -> str:
    return tag_name.replace(":", "_")


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class OneMetaTag:
    """Helper public tag wrapper."""

    name: str
    value: str

    @property
    def normalized_name(self) -> str:
        return _normalize_tag_name(self.name)


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class ValuesGroup:
    """Helper inner wrapper."""

    original: str
    normalized: str


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class TagsGroup:
    """Return struct."""

    title: str = ""
    basic: list[OneMetaTag] = dataclasses.field(default_factory=list)
    open_graph: list[OneMetaTag] = dataclasses.field(default_factory=list)
    twitter: list[OneMetaTag] = dataclasses.field(default_factory=list)
    other: list[OneMetaTag] = dataclasses.field(default_factory=list)


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class SocialMediaSnippet:
    """Social media snippet group."""

    title: str = ""
    description: str = ""
    image: str = ""
    image_width: int = 0
    image_height: int = 0
    url: str = ""


WHAT_ATTRS_IN_SOCIAL_MEDIA_SNIPPET: typing.Final = SocialMediaSnippet.__dataclass_fields__.keys()


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class SnippetGroup:
    """Groupping for social media."""

    open_graph: SocialMediaSnippet = dataclasses.field(default_factory=SocialMediaSnippet)
    twitter: SocialMediaSnippet = dataclasses.field(default_factory=SocialMediaSnippet)


@typing.final
class WhatToParse(enum.IntEnum):
    """Enum for parsing configuration."""

    TITLE = 0
    BASIC = 1
    OPEN_GRAPH = 2
    TWITTER = 3
    OTHER = 4


def _default_what_to_parse() -> tuple["WhatToParse", ...]:
    from . import settings as _settings  # noqa: PLC0415

    return _settings.DEFAULT_PARSE_GROUP


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class PackageOptions:
    """Package configuration options."""

    what_to_parse: tuple[WhatToParse, ...] = dataclasses.field(default_factory=_default_what_to_parse)
    optimize_input: bool = True
    max_prefix_chars: int = 65536
    max_scan_chars: int = 524288
    hard_limit_chars: int | None = None
    boundary_tags: tuple[str, str] = ("</head>", "<body")
