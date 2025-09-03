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
