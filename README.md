# Meta tags parser

[![Test, lint, publish](https://github.com/xfenix/meta-tags-parser/actions/workflows/main.yml/badge.svg)](https://github.com/xfenix/meta-tags-parser/actions/workflows/main.yml)
[![PyPI version](https://badge.fury.io/py/meta-tags-parser.svg)](https://badge.fury.io/py/meta-tags-parser)
[![Downloads](https://pepy.tech/badge/meta-tags-parser)](https://pepy.tech/project/meta-tags-parser)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/xfenix/meta-tags-parser/master/.github/badges/coverage.json)](https://xfenix.github.io/meta-tags-parser/)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
[![Imports: isort](https://img.shields.io/badge/imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://timothycrosley.github.io/isort/)

Fast, modern, pure Python meta tag parser and snippet creator with full support for type annotations.
The base package ships with `py.typed` and provides structured output. No jelly dicts—only typed structures!
If you want to see what social media snippets look like, check the example:
![](https://raw.githubusercontent.com/xfenix/meta-tags-parser/master/social-media-snippets.png)

## Requirements
* Python 3.9+
* [HTTPX](https://www.python-httpx.org/)
* [selectolax](https://github.com/rushter/selectolax)

## Install

`pip install meta-tags-parser`

## Usage

### TL;DR

1. Parse meta tags from a source:

   ```python
   from meta_tags_parser import parse_meta_tags_from_source, structs


   desired_result: structs.TagsGroup = parse_meta_tags_from_source("""... html source ...""")
   # desired_result is what you want
   ```

1. Parse meta tags from a URL:

   ```python
   from meta_tags_parser import parse_tags_from_url, parse_tags_from_url_async, structs


   desired_result: structs.TagsGroup = parse_tags_from_url("https://xfenix.ru")
   # and async variant
   desired_result: structs.TagsGroup = await parse_tags_from_url_async("https://xfenix.ru")
   # desired_result is what you want in both cases
   ```

1. Parse a social media snippet from a source:

   ```python
   from meta_tags_parser import parse_snippets_from_source, structs


   snippet_obj: structs.SnippetGroup = parse_snippets_from_source("""... html source ...""")
   # snippet_obj is what you want
   # access like snippet_obj.open_graph.title, ...
   ```

1. Parse a social media snippet from a URL:

   ```python
   from meta_tags_parser import parse_snippets_from_url, parse_snippets_from_url_async, structs


   snippet_obj: structs.SnippetGroup = parse_snippets_from_url("https://xfenix.ru")
   # and async variant
   snippet_obj: structs.SnippetGroup = await parse_snippets_from_url_async("https://xfenix.ru")
   # snippet_obj is what you want
   # access like snippet_obj.open_graph.title, ...
   ```

**Huge note**: the `*_from_url` functions are provided only for convenience and are very error-prone, so any reconnection or error handling is entirely up to you.
I also avoid adding heavy dependencies to ensure robust connections, since most users don't expect that from this library. If you really need that, contact me.

### Basic snippet parsing

Let's say you want to extract a snippet for Twitter from an HTML page:

```python
from meta_tags_parser import parse_snippets_from_source, structs


my_result: structs.SnippetGroup = parse_snippets_from_source("""
    <meta property="og:card" content="summary_large_image">
    <meta property="og:url" content="https://github.com/">
    <meta property="og:title" content="Hello, my friend">
    <meta property="og:description" content="Content here, yehehe">
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://github.com/">
    <meta property="twitter:title" content="Hello, my friend">
    <meta property="twitter:description" content="Content here, yehehe">
""")

print(my_result)
# What will be printed:
"""
SnippetGroup(
    open_graph=SocialMediaSnippet(
        title='Hello, my friend',
        description='Content here, yehehe',
        image='',
        url='https://github.com/'
    ),
    twitter=SocialMediaSnippet(
        title='Hello, my friend',
        description='Content here, yehehe',
        image='',
        url='https://github.com/'
    )
)
"""
# You can access attributes like this
my_result.open_graph.title
my_result.twitter.image
# All fields are required and will always be available, even if they contain no data
# So you don't need to worry about attribute existence (though you may need to check their values)
```

### Basic meta tag parsing

The main function is `parse_meta_tags_from_source`. Use it like this:

```python
from meta_tags_parser import parse_meta_tags_from_source, structs


my_result: structs.TagsGroup = parse_meta_tags_from_source("""... html source ...""")
print(my_result)

# What will be printed:
"""
structs.TagsGroup(
    title="...",
    twitter=[
        structs.OneMetaTag(
            name="title", value="Hello",
            ...
        )
    ],
    open_graph=[
        structs.OneMetaTag(
            name="title", value="Hello",
            ...
        )
    ],
    basic=[
        structs.OneMetaTag(
            name="title", value="Hello",
            ...
        )
    ],
    other=[
        structs.OneMetaTag(
            name="article:name", value="Hello",
            ...
        )
    ]
)
"""
```

As you can see from this example, we don't use any jelly dicts—only structured dataclasses. Let's see another example:

```python
from meta_tags_parser import parse_meta_tags_from_source, structs


my_result: structs.TagsGroup = parse_meta_tags_from_source("""
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://github.com/">
    <meta property="twitter:title" content="Hello, my friend">
    <meta property="twitter:description" content="Content here, yehehe">
""")

print(my_result)
# What will be printed:
"""
TagsGroup(
    title='',
    basic=[],
    open_graph=[],
    twitter=[
        OneMetaTag(name='card', value='summary_large_image'),
        OneMetaTag(name='url', value='https://github.com/'),
        OneMetaTag(name='title', value='Hello, my friend'),
        OneMetaTag(name='description', value='Content here, yehehe')
    ],
    other=[]
)
"""

for one_tag in my_result.twitter:
    if one_tag.name == "title":
        print(one_tag.value)
# What will be printed:
"""
Hello, my friend
"""
```

### Improving speed

You can specify exactly what to parse:

```python
from meta_tags_parser import parse_meta_tags_from_source, structs


result: structs.TagsGroup = parse_meta_tags_from_source("""... source ...""",
    what_to_parse=(WhatToParse.TITLE, WhatToParse.BASIC, WhatToParse.OPEN_GRAPH, WhatToParse.TWITTER, WhatToParse.OTHER)
)
```

Reducing this tuple of parsing requirements may increase overall parsing speed.

## Important notes
* Any name in a meta tag (name or property attribute) is lowercased
* `og:` and `twitter:` prefixes are stripped from the original attributes, and the dataclass structures carry this information.
* HTML is parsed with [selectolax](https://github.com/rushter/selectolax)'s `LexborHTMLParser`.
  It is fast and tolerant but does not emulate a browser,
  so extremely malformed markup or tags generated by JavaScript may not be handled.
  If the parser encounters a meta tag with property `og:name`, it will appear in the `my_result.open_graph` list
- The page title (e.g., `<title>Something</title>`) is available as the string `my_result.title` (you'll receive `Something`)
- "Standard" tags like `title` and `description` (see the full list in [./meta_tags_parser/structs.py](./meta_tags_parser/structs.py) in the `BASIC_META_TAGS` constant)
  are available as a list in `my_result.basic`
- Other tags are available as a list in `my_result.other`, and their names are preserved, unlike the `og:`/`twitter:` behavior
- For structured snippets, use the `parse_snippets_from_source` function

# Changelog

See the release page at https://github.com/xfenix/meta-tags-parser/releases/.
