"""Main parsing module."""
import enum
import typing
from dataclasses import dataclass


@dataclass
class OneMetaTag:
    """Helper public tag wrapper."""

    name: str
    value: str


@dataclass
class ValuesGroup:
    """Helper inner wrapper."""

    original: str
    normalized: str


class TagsGroup:
    """Return struct."""

    title: str = ""
    basic: list[OneMetaTag] = []
    og: list[OneMetaTag] = []
    twitter: list[OneMetaTag] = []
    other: list[OneMetaTag] = []


class WhatToParse(enum.IntEnum):
    """Enum for parsing configuration."""

    TITLE: int = 0
    BASIC: int = 1
    OG: int = 2
    TWITTER: int = 3
    OTHER: int = 4


BASIC_META_TAGS: typing.Final[tuple[str, ...]] = ("title", "description", "keywords", "robots", "viewport")
SETTINGS_FOR_SOCIAL_MEDIA: typing.Final[dict[typing.Literal[WhatToParse.OG, WhatToParse.TWITTER], dict[str, str]]] = {
    WhatToParse.OG: {"prop": "property", "prefix": "og:"},
    WhatToParse.TWITTER: {"prop": "name", "prefix": "twitter:"},
}
DEFAULT_PARSE_GROUP: typing.Final[tuple[int, ...]] = (
    WhatToParse.TITLE,
    WhatToParse.BASIC,
    WhatToParse.OG,
    WhatToParse.TWITTER,
    WhatToParse.OTHER,
)


__all__ = ["WhatToParse", "OneMetaTag", "TagsGroup"]
