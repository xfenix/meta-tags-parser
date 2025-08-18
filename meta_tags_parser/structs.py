"""Main parsing module."""
from __future__ import annotations
import dataclasses
import enum
import typing


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class OneMetaTag:
    """Helper public tag wrapper."""

    name: str
    value: str


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
