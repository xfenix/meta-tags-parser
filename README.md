# Meta tags parser
[![Test, lint, publish](https://github.com/xfenix/meta-tags-parser/actions/workflows/main.yml/badge.svg)](https://github.com/xfenix/meta-tags-parser/actions/workflows/main.yml)
[![PyPI version](https://badge.fury.io/py/meta-tags-parser.svg)](https://badge.fury.io/py/meta-tags-parser)
[![codecov](https://codecov.io/gh/xfenix/meta-tags-parser/branch/master/graph/badge.svg)](https://codecov.io/gh/xfenix/meta-tags-parser)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
[![Imports: isort](https://img.shields.io/badge/imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://timothycrosley.github.io/isort/)

Fast, modern, pure python meta tags parser and snippet creator with full support of type annotations, py.typed in basic package and structured output. No jelly dicts, only typed structures!  
If you want to see what exactly is social media snippets, look at the example:
![](https://raw.githubusercontent.com/xfenix/meta-tags-parser/master/social-media-snippets.png)

## Requirements
* Python 3.8+
* [Httpx](https://www.python-httpx.org/)

## Install
`pip install meta-tags-parser`

## Usage
### TL:DR
* Parse meta tags from source:
    ```python
    from meta_tags_parser import parse_meta_tags_from_source, structs


    desired_result: structs.TagsGroup = parse_meta_tags_from_source("""... html source ...""")
    # desired_result — is what you want
    ```
* Parse social media snippet from source:
    ```python
    from meta_tags_parser import parse_snippets_from_source, structs


    snippet_obj: structs.SnippetGroup = parse_snippets_from_source("""... html source ...""")
    # snippet_obj — is what you want
    # access like snippet_obj.open_graph.title, ...
    ```
* Parse meta tags from url:
    ```python
    from meta_tags_parser import parse_tags_from_url, parse_tags_from_url_async, structs


    desired_result: structs.TagsGroup = parse_tags_from_url("https://xfenix.ru")
    # and async variant
    desired_result: structs.TagsGroup = await parse_tags_from_url_async("https://xfenix.ru")
    # desired_result — is what you want for both cases
    ```
    Huge note: this functions super stupid and really error prone. I write this only for convenience


### Basic snippets parsing
Lets say you want extract snippet for twitter from html page:
```python
from meta_tags_parser import parse_snippets_from_source, structs


my_result: structs.TagsGroup = parse_snippets_from_source("""
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
# You can access attributes as this
my_result.open_graph.title
my_result.twitter.image
# All fields are necessary and will be always available, even if they have not contain data
# So no need to worry about attributes exsitence (but you may need to check values)
```

### Basic meta tags parsing
Main function is `parse_meta_tags_from_source`. It can be used like this:
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
As you can see from this example, we are not using any jelly dicts, only structured dataclasses. Lets see another example:

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

### If you want to improve speed
You can specify what you want to parse:
```python
from meta_tags_parser import parse_meta_tags_from_source, structs


result: structs.TagsGroup = parse_meta_tags_from_source("""... source ...""",
    what_to_parse=(WhatToParse.TITLE, WhatToParse.BASIC, WhatToParse.OPEN_GRAPH, WhatToParse.TWITTER, WhatToParse.OTHER)
)
```
If you reduce this tuple of parsing requirements it may increase overall parsing speed.

## Important notes
* Any name in meta tag (name or property attribute) will be lowercased
* I decided to strip `og:` and `twitter:` from original attributes, and let dataclass structures carry this information. So if parse meta tag `og:name` in `my_result` variable it will be available as one element of list `my_result.open_graph`
* Title of page (e.g. `<title>Something</title>`) will be available as string `my_result.title`
* «Standart» tags like title, description (check full list here [./meta_tags_parser/structs.py](./meta_tags_parser/structs.py) in constant `BASIC_META_TAGS`) will be available as list in `my_result.basic`
* Other tags will be available as list in `my_result.other` attribute, name of tags will be preserved, unlike `og:`/`twitter:` behaviour
* If you want structured snippets, use `parse_snippets_from_source` function


# Changelog
You can check https://github.com/xfenix/meta-tags-parser/releases/ release page.
