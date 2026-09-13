import typing

import hypothesis
import hypothesis.strategies as st
import pytest

from meta_tags_parser import parse_snippets_from_source, structs


SNIPPET_PAGE_FIXTURE: typing.Final = """
<html><head>
<meta property="og:title" content="Meta Tags — Preview, Edit and Generate">
<meta property="og:description" content="Edit and experiment with your content.">
<meta property="og:url" content="https://metatags.io/">
<meta property="og:image" content="https://metatags.io/assets/preview.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Privet, kak dela to vcelom?">
<meta name="twitter:description" content="Twitter flavoured description.">
<meta name="twitter:url" content="https://metatags.io/">
<meta name="twitter:image" content="https://metatags.io/assets/hm-fail.png">
<meta name="twitter:image:width" content="800">
<meta name="twitter:image:height" content="418">
</head></html>
"""
EXPECTED_SNIPPET_GROUP: typing.Final = structs.SnippetGroup(
    open_graph=structs.SocialMediaSnippet(
        title="Meta Tags — Preview, Edit and Generate",
        description="Edit and experiment with your content.",
        image="https://metatags.io/assets/preview.png",
        image_width=1200,
        image_height=630,
        url="https://metatags.io/",
    ),
    twitter=structs.SocialMediaSnippet(
        title="Privet, kak dela to vcelom?",
        description="Twitter flavoured description.",
        image="https://metatags.io/assets/hm-fail.png",
        image_width=800,
        image_height=418,
        url="https://metatags.io/",
    ),
)
REPEATED_PARSE_COUNT: typing.Final = 3
MAX_GENERATED_DIMENSION: typing.Final = 100_000
UNICODE_DIGITS: typing.Final = st.characters(whitelist_categories=["Nd"])
SAFE_ATTRIBUTE_ALPHABET: typing.Final = st.characters(blacklist_categories=("Cc", "Cs"), blacklist_characters='<>"&')


@pytest.mark.parametrize("_repeat_number", range(REPEATED_PARSE_COUNT))
def test_snippets_are_stable_across_repeated_parsing(_repeat_number: int) -> None:
    assert parse_snippets_from_source(SNIPPET_PAGE_FIXTURE) == EXPECTED_SNIPPET_GROUP


def test_snippets_are_empty_without_social_tags() -> None:
    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(
        '<meta name="twitter:title" content="Hi, whatsup kekeke">'
    )

    assert snippet_result.twitter.title == "Hi, whatsup kekeke"
    assert snippet_result.twitter.image_width == 0
    assert snippet_result.open_graph == structs.SocialMediaSnippet()


def test_first_duplicated_tag_wins() -> None:
    """Social networks treat repeated tags as a list where the first entry is the primary one."""
    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(
        '<meta property="og:title" content="First title">'
        '<meta property="og:title" content="Second title">'
        '<meta property="og:image" content="https://example.com/first.png">'
        '<meta property="og:image:width" content="640">'
        '<meta property="og:image" content="https://example.com/second.png">'
        '<meta property="og:image:width" content="1280">'
    )

    assert snippet_result.open_graph.title == "First title"
    assert snippet_result.open_graph.image == "https://example.com/first.png"
    assert snippet_result.open_graph.image_width == 640


def test_unknown_social_tags_do_not_reach_the_snippet() -> None:
    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(
        '<meta property="og:video:duration" content="754"><meta property="og:audio" content="x.mp3">'
    )

    assert snippet_result.open_graph == structs.SocialMediaSnippet()


def test_snippets_accept_bytes() -> None:
    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(
        '<html><head><meta charset="windows-1251"><meta property="og:title" content="Заголовок"></head></html>'.encode(
            "windows-1251"
        )
    )

    assert snippet_result.open_graph.title == "Заголовок"


@pytest.mark.parametrize(
    ("dimension_text", "expected_width"),
    [
        ("", 0),
        ("   ", 0),
        ("123", 123),
        ("  55  ", 55),
        ("0", 0),
        ("abc", 0),
        ("12.5", 0),
        ("-12", 0),
        ("1200px", 0),
        ("١٢٣", 0),
        ("٥", 0),
        ("²", 0),
    ],
)
def test_image_width_examples(dimension_text: str, expected_width: int) -> None:
    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(
        f'<meta property="twitter:image:width" content="{dimension_text}">'
    )

    assert snippet_result.twitter.image_width == expected_width


@hypothesis.given(
    dimension_text=st.one_of(
        st.integers(min_value=0, max_value=MAX_GENERATED_DIMENSION).map(str),
        st.text(alphabet=UNICODE_DIGITS, min_size=1, max_size=8),
        st.text(alphabet=SAFE_ATTRIBUTE_ALPHABET, max_size=8),
    )
)
def test_image_dimensions_follow_the_ascii_digit_rule(dimension_text: str) -> None:
    """Anything that is not a plain ascii number (unicode digits, units, decimals) becomes a zero."""
    cleaned_text: typing.Final[str] = dimension_text.strip()

    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(
        f'<meta property="og:image:width" content="{dimension_text}">'
    )

    assert snippet_result.open_graph.image_width == (
        int(cleaned_text) if cleaned_text.isascii() and cleaned_text.isdigit() else 0
    )


@hypothesis.settings(max_examples=50)
@hypothesis.given(snippet_title=st.text(alphabet=SAFE_ATTRIBUTE_ALPHABET, max_size=80))
def test_any_title_survives_the_round_trip(snippet_title: str) -> None:
    snippet_result: typing.Final[structs.SnippetGroup] = parse_snippets_from_source(
        f'<meta property="og:title" content="{snippet_title}">'
    )

    assert snippet_result.open_graph.title == snippet_title
