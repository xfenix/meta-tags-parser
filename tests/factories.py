"""Polyfactory factories for the public data model.

They keep property style tests honest: instead of hand writing a handful of settings objects we let
polyfactory build many of them, with the ranges narrowed to values that make sense for a parser.
"""

import random
import typing

from polyfactory.factories import dataclass_factory

from meta_tags_parser import structs


FACTORY_RANDOM_SEED: typing.Final = 20260818
MAX_GENERATED_LIMIT_CHARS: typing.Final = 8192
MIN_GENERATED_LIMIT_CHARS: typing.Final = 16
SHARED_RANDOM_SOURCE: typing.Final = random.Random(FACTORY_RANDOM_SEED)
KNOWN_BOUNDARY_TAG_PAIRS: typing.Final[tuple[tuple[str, str], ...]] = (
    ("</head>", "<body"),
    ("</HEAD>", "<BODY"),
    ("</head>", "<article"),
    ("</title>", "<body"),
)


@typing.final
class SettingsFromUserFactory(dataclass_factory.DataclassFactory[structs.SettingsFromUser]):
    """Build settings objects covering every combination of what_to_parse and slicing limits."""

    __model__ = structs.SettingsFromUser
    __random__ = SHARED_RANDOM_SOURCE

    @classmethod
    def what_to_parse(cls) -> tuple[structs.WhatToParse, ...]:  # noqa: COP009, COP007
        possible_parts: typing.Final[list[structs.WhatToParse]] = list(structs.WhatToParse)
        return tuple(cls.__random__.sample(possible_parts, k=cls.__random__.randint(1, len(possible_parts))))

    @classmethod
    def boundary_tags(cls) -> tuple[str, str]:  # noqa: COP009, COP007
        return cls.__random__.choice(KNOWN_BOUNDARY_TAG_PAIRS)

    @classmethod
    def fallback_limit_chars(cls) -> int:  # noqa: COP009, COP007
        return cls.__random__.randint(MIN_GENERATED_LIMIT_CHARS, MAX_GENERATED_LIMIT_CHARS)

    @classmethod
    def max_scan_chars(cls) -> int:  # noqa: COP009, COP007
        return cls.__random__.randint(MIN_GENERATED_LIMIT_CHARS, MAX_GENERATED_LIMIT_CHARS)

    @classmethod
    def hard_limit_chars(cls) -> int | None:  # noqa: COP009, COP007
        return cls.__random__.choice(
            (None, cls.__random__.randint(MIN_GENERATED_LIMIT_CHARS, MAX_GENERATED_LIMIT_CHARS))
        )
