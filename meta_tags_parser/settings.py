import types
import typing

from . import structs


BASIC_META_TAGS: typing.Final[tuple[str, ...]] = (
    "title",
    "description",
    "keywords",
    "robots",
    "viewport",
)
SETTINGS_FOR_SOCIAL_MEDIA: typing.Final[
    typing.Mapping[
        typing.Literal[structs.WhatToParse.OPEN_GRAPH, structs.WhatToParse.TWITTER],
        typing.Mapping[str, str | tuple[str, ...]],
    ]
] = types.MappingProxyType(
    {
        structs.WhatToParse.OPEN_GRAPH: types.MappingProxyType({"prop": ("property",), "prefix": "og:"}),
        # weird thing about twitter: it use name and property simultaneously
        # i mean name is old format, property is new, but all currently accepted as i see at the moment
        structs.WhatToParse.TWITTER: types.MappingProxyType({"prop": ("name", "property"), "prefix": "twitter:"}),
    }
)
DEFAULT_PARSE_GROUP: typing.Final[tuple[structs.WhatToParse, ...]] = (
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
