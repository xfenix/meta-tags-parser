"""Main parsing module."""
from __future__ import annotations
import dataclasses
import enum


@dataclasses.dataclass
class OneMetaTag:
    """Helper public tag wrapper."""

    name: str
    value: str


@dataclasses.dataclass
class ValuesGroup:
    """Helper inner wrapper."""

    original: str
    normalized: str


@dataclasses.dataclass
class TagsGroup:
    """Return struct."""

    title: str = ""
    basic: list[OneMetaTag] = dataclasses.field(default_factory=list)
    open_graph: list[OneMetaTag] = dataclasses.field(default_factory=list)
    twitter: list[OneMetaTag] = dataclasses.field(default_factory=list)
    other: list[OneMetaTag] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class SocialMediaSnippet:
    """Social media snippet group."""

    title: str = ""
    description: str = ""
    image: str = ""
    image_width: int = 0
    image_height: int = 0
    url: str = ""


@dataclasses.dataclass
class SnippetGroup:
    """Groupping for social media."""

    open_graph: SocialMediaSnippet = dataclasses.field(default_factory=SocialMediaSnippet)
    twitter: SocialMediaSnippet = dataclasses.field(default_factory=SocialMediaSnippet)


class WhatToParse(enum.IntEnum):
    """Enum for parsing configuration."""

    TITLE: int = 0
    BASIC: int = 1
    OPEN_GRAPH: int = 2
    TWITTER: int = 3
    OTHER: int = 4
