"""Package settings."""
from __future__ import annotations
import typing

from . import structs


BASIC_META_TAGS: typing.Final[tuple[str, ...]] = ("title", "description", "keywords", "robots", "viewport")
SETTINGS_FOR_SOCIAL_MEDIA: typing.Final[
    dict[
        typing.Literal[structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER], dict[str, typing.Union[str, tuple]]
    ]
] = {
    structs.WhatToParse.OPEN_GRAPH: {"prop": ("property",), "prefix": "og:"},
    # weird thing about twitter: it use name and property simultaneously
    # i mean name is old format, property is new, but all currently accepted as i see at the moment
    structs.WhatToParse.TWITTER: {"prop": ("name", "property"), "prefix": "twitter:"},
}
DEFAULT_PARSE_GROUP: typing.Final[tuple[int, ...]] = (
    structs.WhatToParse.TITLE,
    structs.WhatToParse.BASIC,
    structs.WhatToParse.OPEN_GRAPH,
    structs.WhatToParse.TWITTER,
    structs.WhatToParse.OTHER,
)
SOCIAL_MEDIA_SNIPPET_WHAT_ATTRS_TO_COPY: typing.Final[tuple[str, ...]] = (
    "title",
    "description",
    "url",
    "image",
    "image:width",
    "image:height",
)
