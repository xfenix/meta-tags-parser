"""Main parsing module."""
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


class WhatToParse:
    """Enum for parsing configuration."""

    TITLE: int = 0
    BASIC: int = 1
    OG: int = 2
    TWITTER: int = 3


DEFAULT_PARSE_GROUP: tuple[int, ...] = (
    WhatToParse.TITLE,
    WhatToParse.BASIC,
    WhatToParse.OG,
    WhatToParse.TWITTER,
)


__all__ = ["WhatToParse", "OneMetaTag", "TagsGroup"]
