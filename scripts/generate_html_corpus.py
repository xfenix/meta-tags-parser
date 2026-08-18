"""Build the real-world shaped HTML corpus used by the integration tests.

The corpus mimics what the parser actually meets in production: news portals, shops, video pages and
single page applications, in fifteen languages, with the markup quirks real sites ship (uppercase
tags, single quoted attributes, duplicated Open Graph tags, meta tags after the head, legacy
charsets, byte order marks, emoji, right to left text and so on).

Every page is generated from a declarative list of planned meta tags, so the expected parse result is
derived from what was written into the page, not from what the parser returns. The pages are stored
gzipped (``*.html.gz``) because a realistic corpus of a hundred big pages is tens of megabytes raw.

Regenerate with::

    uv run python -m scripts.generate_html_corpus
"""

import base64
import dataclasses
import gzip
import html
import itertools
import json
import pathlib
import random
import typing

from scripts import corpus_locales


CORPUS_DIRECTORY: typing.Final = pathlib.Path(__file__).resolve().parent.parent / "tests" / "html_corpus"
EXPECTATIONS_FILE_NAME: typing.Final = "expectations.json"
BASIC_META_TAG_NAMES: typing.Final[tuple[str, ...]] = ("title", "description", "keywords", "robots", "viewport")
SNIPPET_FIELD_NAMES: typing.Final[tuple[str, ...]] = (
    "title",
    "description",
    "image",
    "image_width",
    "image_height",
    "url",
)
DIMENSION_FIELD_NAMES: typing.Final[frozenset[str]] = frozenset(("image_width", "image_height"))
ARCHETYPE_NAMES: typing.Final[tuple[str, ...]] = (
    "news_article",
    "ecommerce_product",
    "video_page",
    "wordpress_blog_post",
    "documentation_page",
    "spa_hydration",
    "forum_thread",
    "marketing_landing",
    "government_portal",
    "media_gallery",
)
QUIRK_NAMES: typing.Final[tuple[str, ...]] = (
    "plain_markup",
    "upper_case_markup",
    "single_quoted_attributes",
    "unquoted_attributes",
    "duplicated_open_graph",
    "meta_inside_body",
    "empty_content_values",
    "legacy_encoding",
    "byte_order_mark",
    "whitespace_padded_title",
    "escaped_entities_title",
    "multiline_content",
    "open_graph_via_name_attribute",
    "missing_head_closing_tag",
    "without_boundary_tags",
    "emoji_content",
    "http_equiv_charset",
    "itemprop_markup",
    "very_long_content",
    "dotted_capital_letter",
)
TOTAL_PAGES_COUNT: typing.Final = 100
FILLER_SCALE_STEPS: typing.Final[tuple[int, ...]] = (1, 2, 5, 12, 40)
SMALL_FILLER_SCALE: typing.Final = 1
LONG_CONTENT_REPEATS: typing.Final = 90
BASE64_BLOB_BYTES: typing.Final = 512
CORPUS_RANDOM_SEED: typing.Final = 20260818
LEGACY_ENCODING_STRIDE: typing.Final = 4


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class PlannedMetaTag:
    """One meta tag as it will be written into the page, plus how it should be parsed back."""

    attribute_kind: str
    attribute_value: str
    content_value: str = ""
    omit_content: bool = False
    placed_in_body: bool = False
    quote_override: str | None = None


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class PageBlueprint:
    """Everything that makes one corpus page unique."""

    page_slug: str
    locale_key: str
    archetype_name: str
    quirk_name: str
    filler_scale: int
    use_legacy_encoding: bool


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class PageMarkupStyle:
    """How the markup of a single page is rendered."""

    quote_character: str = '"'
    upper_case_markup: bool = False


def _choose_locale_entry(locale_key: str) -> corpus_locales.LocaleContent:
    return corpus_locales.ALL_LOCALES[locale_key]


def _render_meta_tag(one_meta_tag: PlannedMetaTag, markup_style: PageMarkupStyle) -> str:
    quote_character: typing.Final[str] = (
        one_meta_tag.quote_override if one_meta_tag.quote_override is not None else markup_style.quote_character
    )
    attribute_name: typing.Final[str] = (
        one_meta_tag.attribute_kind.upper() if markup_style.upper_case_markup else one_meta_tag.attribute_kind
    )
    attribute_value: typing.Final[str] = (
        one_meta_tag.attribute_value.upper() if markup_style.upper_case_markup else one_meta_tag.attribute_value
    )
    content_name: typing.Final[str] = "CONTENT" if markup_style.upper_case_markup else "content"
    tag_name: typing.Final[str] = "META" if markup_style.upper_case_markup else "meta"
    rendered_parts: typing.Final[list[str]] = [
        f"{attribute_name}={quote_character}{html.escape(attribute_value)}{quote_character}"
    ]
    if not one_meta_tag.omit_content:
        rendered_parts.append(
            f"{content_name}={quote_character}{html.escape(one_meta_tag.content_value)}{quote_character}"
        )
    return f"<{tag_name} {' '.join(rendered_parts)}>"


def _build_social_tag_pairs(
    locale_entry: corpus_locales.LocaleContent,
    chosen_headline: str,
    *,
    chosen_description: str,
    page_address: str,
    open_graph_type: str,
) -> list[PlannedMetaTag]:
    image_address: typing.Final[str] = f"https://{locale_entry.site_domain}/static/social-preview.jpg"
    return [
        PlannedMetaTag(attribute_kind="property", attribute_value="og:type", content_value=open_graph_type),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:locale", content_value=locale_entry.locale_code),
        PlannedMetaTag(
            attribute_kind="property", attribute_value="og:site_name", content_value=locale_entry.site_title
        ),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:title", content_value=chosen_headline),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:description", content_value=chosen_description),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:url", content_value=page_address),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:image", content_value=image_address),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:image:width", content_value="1200"),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:image:height", content_value="630"),
        PlannedMetaTag(attribute_kind="name", attribute_value="twitter:card", content_value="summary_large_image"),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="twitter:site", content_value="@" + locale_entry.locale_code
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="twitter:title", content_value=chosen_headline),
        PlannedMetaTag(attribute_kind="name", attribute_value="twitter:description", content_value=chosen_description),
        PlannedMetaTag(attribute_kind="name", attribute_value="twitter:image", content_value=image_address),
        PlannedMetaTag(attribute_kind="name", attribute_value="twitter:url", content_value=page_address),
    ]


def _build_head_of_news_article(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    chosen_headline: typing.Final[str] = random_source.choice(locale_entry.headlines)
    chosen_description: typing.Final[str] = random_source.choice(locale_entry.descriptions)
    page_address: typing.Final[str] = f"https://{locale_entry.site_domain}/news/2026/energy-storage"
    return [
        PlannedMetaTag(attribute_kind="charset", attribute_value="utf-8", omit_content=True),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="viewport", content_value="width=device-width, initial-scale=1"
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value=chosen_description),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="keywords", content_value=", ".join(locale_entry.keyword_list)
        ),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="robots", content_value="index, follow, max-image-preview:large"
        ),
        PlannedMetaTag(
            attribute_kind="name",
            attribute_value="author",
            content_value=random_source.choice(locale_entry.author_names),
        ),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="news_keywords", content_value=locale_entry.keyword_list[0]
        ),
        *_build_social_tag_pairs(
            locale_entry,
            chosen_headline,
            chosen_description=chosen_description,
            page_address=page_address,
            open_graph_type="article",
        ),
        PlannedMetaTag(
            attribute_kind="property",
            attribute_value="article:published_time",
            content_value="2026-03-14T08:30:00+03:00",
        ),
        PlannedMetaTag(
            attribute_kind="property", attribute_value="article:section", content_value=locale_entry.section_names[0]
        ),
    ]


def _build_head_of_ecommerce_product(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    chosen_headline: typing.Final[str] = random_source.choice(locale_entry.headlines)
    chosen_description: typing.Final[str] = random_source.choice(locale_entry.descriptions)
    page_address: typing.Final[str] = f"https://{locale_entry.site_domain}/shop/item/884213"
    return [
        PlannedMetaTag(attribute_kind="charset", attribute_value="utf-8", omit_content=True),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="viewport", content_value="width=device-width, initial-scale=1"
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value=chosen_description),
        PlannedMetaTag(attribute_kind="name", attribute_value="robots", content_value="index, follow"),
        *_build_social_tag_pairs(
            locale_entry,
            chosen_headline,
            chosen_description=chosen_description,
            page_address=page_address,
            open_graph_type="product",
        ),
        PlannedMetaTag(attribute_kind="property", attribute_value="product:price:amount", content_value="129.99"),
        PlannedMetaTag(attribute_kind="property", attribute_value="product:price:currency", content_value="EUR"),
        PlannedMetaTag(attribute_kind="property", attribute_value="product:availability", content_value="in stock"),
        PlannedMetaTag(attribute_kind="itemprop", attribute_value="sku", content_value="884213"),
        PlannedMetaTag(attribute_kind="name", attribute_value="theme-color", content_value="#0b7285"),
    ]


def _build_head_of_video_page(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    chosen_headline: typing.Final[str] = random_source.choice(locale_entry.headlines)
    chosen_description: typing.Final[str] = random_source.choice(locale_entry.descriptions)
    page_address: typing.Final[str] = f"https://{locale_entry.site_domain}/watch/vd-77123"
    return [
        PlannedMetaTag(attribute_kind="charset", attribute_value="utf-8", omit_content=True),
        PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value=chosen_description),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="viewport", content_value="width=device-width, initial-scale=1"
        ),
        *_build_social_tag_pairs(
            locale_entry,
            chosen_headline,
            chosen_description=chosen_description,
            page_address=page_address,
            open_graph_type="video.other",
        ),
        PlannedMetaTag(
            attribute_kind="property",
            attribute_value="og:video",
            content_value=f"https://{locale_entry.site_domain}/media/vd-77123.mp4",
        ),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:video:duration", content_value="754"),
        PlannedMetaTag(attribute_kind="name", attribute_value="twitter:player:width", content_value="1280"),
        PlannedMetaTag(attribute_kind="name", attribute_value="twitter:player:height", content_value="720"),
    ]


def _build_head_of_wordpress_blog_post(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    chosen_headline: typing.Final[str] = random_source.choice(locale_entry.headlines)
    chosen_description: typing.Final[str] = random_source.choice(locale_entry.descriptions)
    page_address: typing.Final[str] = f"https://{locale_entry.site_domain}/blog/commuter-bike-guide"
    return [
        PlannedMetaTag(attribute_kind="charset", attribute_value="UTF-8", omit_content=True),
        PlannedMetaTag(attribute_kind="name", attribute_value="generator", content_value="WordPress 6.7.1"),
        PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value=chosen_description),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="robots", content_value="max-snippet:-1, max-video-preview:-1"
        ),
        *_build_social_tag_pairs(
            locale_entry,
            chosen_headline,
            chosen_description=chosen_description,
            page_address=page_address,
            open_graph_type="article",
        ),
        PlannedMetaTag(
            attribute_kind="property",
            attribute_value="article:modified_time",
            content_value="2026-04-02T11:05:22+00:00",
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="msapplication-TileColor", content_value="#ffffff"),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="twitter:label1", content_value=locale_entry.section_names[1]
        ),
        PlannedMetaTag(
            attribute_kind="name",
            attribute_value="twitter:data1",
            content_value=random_source.choice(locale_entry.author_names),
        ),
    ]


def _build_head_of_documentation_page(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    chosen_headline: typing.Final[str] = random_source.choice(locale_entry.headlines)
    chosen_description: typing.Final[str] = random_source.choice(locale_entry.descriptions)
    page_address: typing.Final[str] = f"https://{locale_entry.site_domain}/docs/reference/http-api"
    return [
        PlannedMetaTag(attribute_kind="charset", attribute_value="utf-8", omit_content=True),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="viewport", content_value="width=device-width,initial-scale=1"
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value=chosen_description),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="docsearch:language", content_value=locale_entry.language_code
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="docsearch:version", content_value="4.2"),
        PlannedMetaTag(attribute_kind="name", attribute_value="color-scheme", content_value="light dark"),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:title", content_value=chosen_headline),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:description", content_value=chosen_description),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:url", content_value=page_address),
        PlannedMetaTag(attribute_kind="name", attribute_value="twitter:card", content_value="summary"),
    ]


def _build_head_of_spa_hydration(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    chosen_headline: typing.Final[str] = random_source.choice(locale_entry.headlines)
    chosen_description: typing.Final[str] = random_source.choice(locale_entry.descriptions)
    page_address: typing.Final[str] = f"https://{locale_entry.site_domain}/app/dashboard"
    return [
        PlannedMetaTag(attribute_kind="charset", attribute_value="utf-8", omit_content=True),
        PlannedMetaTag(
            attribute_kind="name",
            attribute_value="viewport",
            content_value="width=device-width, initial-scale=1, viewport-fit=cover",
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="next-head-count", content_value="17"),
        PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value=chosen_description),
        *_build_social_tag_pairs(
            locale_entry,
            chosen_headline,
            chosen_description=chosen_description,
            page_address=page_address,
            open_graph_type="website",
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="apple-mobile-web-app-capable", content_value="yes"),
        PlannedMetaTag(attribute_kind="name", attribute_value="mobile-web-app-capable", content_value="yes"),
    ]


def _build_head_of_forum_thread(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    chosen_headline: typing.Final[str] = random_source.choice(locale_entry.headlines)
    chosen_description: typing.Final[str] = random_source.choice(locale_entry.descriptions)
    page_address: typing.Final[str] = f"https://{locale_entry.site_domain}/t/thread-91824/12"
    return [
        PlannedMetaTag(attribute_kind="charset", attribute_value="utf-8", omit_content=True),
        PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value=chosen_description),
        PlannedMetaTag(attribute_kind="name", attribute_value="robots", content_value="noindex, follow"),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="viewport", content_value="width=device-width, initial-scale=1"
        ),
        *_build_social_tag_pairs(
            locale_entry,
            chosen_headline,
            chosen_description=chosen_description,
            page_address=page_address,
            open_graph_type="website",
        ),
        PlannedMetaTag(
            attribute_kind="property",
            attribute_value="og:image",
            content_value=f"https://{locale_entry.site_domain}/avatars/user-2281.png",
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="discourse_theme_id", content_value="4"),
    ]


def _build_head_of_marketing_landing(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    chosen_headline: typing.Final[str] = random_source.choice(locale_entry.headlines)
    chosen_description: typing.Final[str] = random_source.choice(locale_entry.descriptions)
    page_address: typing.Final[str] = f"https://{locale_entry.site_domain}/pricing"
    return [
        PlannedMetaTag(attribute_kind="charset", attribute_value="utf-8", omit_content=True),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="viewport", content_value="width=device-width, initial-scale=1"
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value=chosen_description),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="keywords", content_value=", ".join(locale_entry.keyword_list[:3])
        ),
        *_build_social_tag_pairs(
            locale_entry,
            chosen_headline,
            chosen_description=chosen_description,
            page_address=page_address,
            open_graph_type="website",
        ),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="facebook-domain-verification", content_value="qz18ptr4m0"
        ),
        PlannedMetaTag(attribute_kind="name", attribute_value="yandex-verification", content_value="8d1f0c4b7a2e"),
    ]


def _build_head_of_government_portal(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    chosen_headline: typing.Final[str] = random_source.choice(locale_entry.headlines)
    chosen_description: typing.Final[str] = random_source.choice(locale_entry.descriptions)
    page_address: typing.Final[str] = f"https://{locale_entry.site_domain}/services/permits"
    return [
        PlannedMetaTag(attribute_kind="charset", attribute_value="utf-8", omit_content=True),
        PlannedMetaTag(attribute_kind="http-equiv", attribute_value="X-UA-Compatible", content_value="IE=edge"),
        PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value=chosen_description),
        PlannedMetaTag(attribute_kind="name", attribute_value="viewport", content_value="width=device-width"),
        PlannedMetaTag(attribute_kind="name", attribute_value="dc.language", content_value=locale_entry.locale_code),
        PlannedMetaTag(attribute_kind="name", attribute_value="dc.publisher", content_value=locale_entry.site_title),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:title", content_value=chosen_headline),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:url", content_value=page_address),
        PlannedMetaTag(attribute_kind="property", attribute_value="og:description", content_value=chosen_description),
    ]


def _build_head_of_media_gallery(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    chosen_headline: typing.Final[str] = random_source.choice(locale_entry.headlines)
    chosen_description: typing.Final[str] = random_source.choice(locale_entry.descriptions)
    page_address: typing.Final[str] = f"https://{locale_entry.site_domain}/gallery/city-at-night"
    extra_images: typing.Final[list[PlannedMetaTag]] = []
    for one_image_number in range(2, 6):
        extra_images.append(
            PlannedMetaTag(
                attribute_kind="property",
                attribute_value="og:image",
                content_value=f"https://{locale_entry.site_domain}/gallery/city-{one_image_number}.jpg",
            )
        )
        extra_images.append(
            PlannedMetaTag(attribute_kind="property", attribute_value="og:image:width", content_value="2048")
        )
    return [
        PlannedMetaTag(attribute_kind="charset", attribute_value="utf-8", omit_content=True),
        PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value=chosen_description),
        PlannedMetaTag(
            attribute_kind="name", attribute_value="viewport", content_value="width=device-width, initial-scale=1"
        ),
        *_build_social_tag_pairs(
            locale_entry,
            chosen_headline,
            chosen_description=chosen_description,
            page_address=page_address,
            open_graph_type="website",
        ),
        *extra_images,
    ]


ARCHETYPE_BUILDERS: typing.Final[
    typing.Mapping[str, typing.Callable[[corpus_locales.LocaleContent, random.Random], list[PlannedMetaTag]]]
] = {
    "news_article": _build_head_of_news_article,
    "ecommerce_product": _build_head_of_ecommerce_product,
    "video_page": _build_head_of_video_page,
    "wordpress_blog_post": _build_head_of_wordpress_blog_post,
    "documentation_page": _build_head_of_documentation_page,
    "spa_hydration": _build_head_of_spa_hydration,
    "forum_thread": _build_head_of_forum_thread,
    "marketing_landing": _build_head_of_marketing_landing,
    "government_portal": _build_head_of_government_portal,
    "media_gallery": _build_head_of_media_gallery,
}


def _choose_markup_style(quirk_name: str) -> PageMarkupStyle:
    if quirk_name == "upper_case_markup":
        return PageMarkupStyle(upper_case_markup=True)
    if quirk_name == "single_quoted_attributes":
        return PageMarkupStyle(quote_character="'")
    return PageMarkupStyle()


def _choose_page_title(
    locale_entry: corpus_locales.LocaleContent,
    quirk_name: str,
    *,
    random_source: random.Random,
) -> str:
    plain_title: typing.Final[str] = f"{random_source.choice(locale_entry.headlines)} | {locale_entry.site_title}"
    if quirk_name == "whitespace_padded_title":
        return f"\n    {plain_title}\n\t "
    if quirk_name == "escaped_entities_title":
        return f'{plain_title} <AT&T> "quoted"'
    if quirk_name == "emoji_content":
        return f"🔥 {plain_title} 🚲"
    if quirk_name == "dotted_capital_letter":
        return f"İstanbul & Diyarbakır — {plain_title}"
    return plain_title


def _build_quirk_specific_tags(
    locale_entry: corpus_locales.LocaleContent,
    quirk_name: str,
    *,
    random_source: random.Random,
) -> list[PlannedMetaTag]:
    long_description: typing.Final[str] = " ".join(locale_entry.paragraphs) * LONG_CONTENT_REPEATS
    quirk_specific_tags: typing.Final[dict[str, list[PlannedMetaTag]]] = {
        "unquoted_attributes": [
            PlannedMetaTag(
                attribute_kind="property",
                attribute_value="og:audio",
                content_value=f"https://{locale_entry.site_domain}/audio/intro.mp3",
                quote_override="",
            ),
            PlannedMetaTag(
                attribute_kind="name", attribute_value="referrer", content_value="no-referrer", quote_override=""
            ),
        ],
        "duplicated_open_graph": [
            PlannedMetaTag(
                attribute_kind="property",
                attribute_value="og:title",
                content_value=f"{locale_entry.headlines[-1]} (duplicate)",
            ),
            PlannedMetaTag(
                attribute_kind="property", attribute_value="og:description", content_value=locale_entry.descriptions[-1]
            ),
            PlannedMetaTag(
                attribute_kind="name", attribute_value="twitter:title", content_value=locale_entry.headlines[-1]
            ),
            PlannedMetaTag(attribute_kind="name", attribute_value="description", content_value="duplicate description"),
        ],
        "meta_inside_body": [
            PlannedMetaTag(
                attribute_kind="property",
                attribute_value="og:audio",
                content_value=f"https://{locale_entry.site_domain}/audio/late.mp3",
                placed_in_body=True,
            ),
            PlannedMetaTag(
                attribute_kind="name",
                attribute_value="twitter:creator",
                content_value="@" + locale_entry.language_code,
                placed_in_body=True,
            ),
            PlannedMetaTag(
                attribute_kind="name",
                attribute_value="rating",
                content_value="general",
                placed_in_body=True,
            ),
        ],
        "empty_content_values": [
            PlannedMetaTag(attribute_kind="property", attribute_value="og:audio", content_value=""),
            PlannedMetaTag(attribute_kind="name", attribute_value="twitter:creator", content_value=""),
            PlannedMetaTag(attribute_kind="name", attribute_value="rating", content_value=""),
            PlannedMetaTag(attribute_kind="name", attribute_value="classification", omit_content=True),
        ],
        "multiline_content": [
            PlannedMetaTag(
                attribute_kind="property",
                attribute_value="og:audio",
                content_value=f"{locale_entry.paragraphs[0]}\n        {locale_entry.paragraphs[1]}",
            )
        ],
        "open_graph_via_name_attribute": [
            PlannedMetaTag(
                attribute_kind="name", attribute_value="og:audio", content_value=locale_entry.descriptions[0]
            ),
            PlannedMetaTag(
                attribute_kind="name", attribute_value="og:street_address", content_value=locale_entry.section_names[0]
            ),
        ],
        "itemprop_markup": [
            PlannedMetaTag(attribute_kind="itemprop", attribute_value="name", content_value=locale_entry.site_title),
            PlannedMetaTag(
                attribute_kind="itemprop", attribute_value="description", content_value=locale_entry.descriptions[0]
            ),
            PlannedMetaTag(attribute_kind="itemprop", attribute_value="ratingValue", content_value="4.6"),
        ],
        "very_long_content": [
            PlannedMetaTag(attribute_kind="name", attribute_value="abstract", content_value=long_description)
        ],
        "emoji_content": [
            PlannedMetaTag(
                attribute_kind="property",
                attribute_value="og:audio",
                content_value=f"🎧 {random_source.choice(locale_entry.descriptions)} ✅",
            )
        ],
        "dotted_capital_letter": [
            PlannedMetaTag(
                attribute_kind="name",
                attribute_value="geo.placename",
                content_value="İstanbul İzmir Diyarbakır",
            )
        ],
        "http_equiv_charset": [
            PlannedMetaTag(
                attribute_kind="http-equiv", attribute_value="refresh", content_value="3600;url=/session-expired"
            )
        ],
    }
    return quirk_specific_tags.get(quirk_name, [])


def _override_charset_declaration(
    planned_tags: list[PlannedMetaTag],
    encoding_name: str,
    *,
    quirk_name: str,
) -> list[PlannedMetaTag]:
    charset_tag: typing.Final[PlannedMetaTag] = (
        PlannedMetaTag(
            attribute_kind="http-equiv",
            attribute_value="Content-Type",
            content_value=f"text/html; charset={encoding_name}",
        )
        if quirk_name == "http_equiv_charset"
        else PlannedMetaTag(attribute_kind="charset", attribute_value=encoding_name, omit_content=True)
    )
    return [charset_tag, *(one_meta_tag for one_meta_tag in planned_tags if one_meta_tag.attribute_kind != "charset")]


def _choose_encoding_name(locale_entry: corpus_locales.LocaleContent, one_blueprint: PageBlueprint) -> str:
    if not one_blueprint.use_legacy_encoding or locale_entry.legacy_encoding is None:
        return "utf-8"
    return locale_entry.legacy_encoding


def _build_head_filler(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
    *,
    filler_scale: int,
) -> str:
    style_rules: typing.Final[list[str]] = [
        f".block-{one_rule_number}{{margin:{one_rule_number % 9}px;padding:{one_rule_number % 5}px;"
        f"color:#{one_rule_number % 10}{one_rule_number % 8}{one_rule_number % 7}aef}}"
        for one_rule_number in range(filler_scale * 40)
    ]
    preload_links: typing.Final[list[str]] = [
        f'<link rel="preload" as="font" crossorigin href="/assets/font-{one_link_number}.woff2">'
        for one_link_number in range(filler_scale * 3)
    ]
    linked_data: typing.Final[dict[str, typing.Any]] = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": random_source.choice(locale_entry.headlines),
        "description": random_source.choice(locale_entry.descriptions),
        "inLanguage": locale_entry.language_code,
        "author": [{"@type": "Person", "name": one_author} for one_author in locale_entry.author_names],
        "articleBody": " ".join(locale_entry.paragraphs * filler_scale),
        "keywords": list(locale_entry.keyword_list),
    }
    return "\n".join(
        [
            "<style>" + "".join(style_rules) + "</style>",
            *preload_links,
            '<script type="application/ld+json">' + json.dumps(linked_data, ensure_ascii=False) + "</script>",
        ]
    )


def _build_body_filler(
    locale_entry: corpus_locales.LocaleContent,
    random_source: random.Random,
    *,
    filler_scale: int,
) -> str:
    encoded_blob: typing.Final[str] = base64.b64encode(
        random_source.randbytes(BASE64_BLOB_BYTES * filler_scale)
    ).decode("ascii")
    article_paragraphs: typing.Final[list[str]] = [
        f'<p class="block-{one_paragraph_number}">{html.escape(one_paragraph)}</p>'
        for one_paragraph_number, one_paragraph in enumerate(locale_entry.paragraphs * filler_scale * 4)
    ]
    navigation_items: typing.Final[str] = "".join(
        f'<li><a href="/{one_section.lower()}">{html.escape(one_section)}</a></li>'
        for one_section in locale_entry.section_names
    )
    hydration_state: typing.Final[dict[str, typing.Any]] = {
        "locale": locale_entry.locale_code,
        "sections": list(locale_entry.section_names),
        "items": [
            {"id": one_item_number, "title": random_source.choice(locale_entry.headlines)}
            for one_item_number in range(filler_scale * 12)
        ],
    }
    return "\n".join(
        [
            f"<nav><ul>{navigation_items}</ul></nav>",
            f"<article>{''.join(article_paragraphs)}</article>",
            f'<img alt="preview" src="data:image/png;base64,{encoded_blob}">',
            "<script>window.__STATE__=" + json.dumps(hydration_state, ensure_ascii=False) + ";</script>",
        ]
    )


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class PageDocumentParts:
    """Rendered pieces of one page, kept together to keep the render signature small."""

    page_title: str
    head_markup: str
    body_markup: str
    head_filler: str
    body_filler: str


def _render_page_document(
    locale_entry: corpus_locales.LocaleContent,
    quirk_name: str,
    *,
    document_parts: PageDocumentParts,
) -> str:
    escaped_title: typing.Final[str] = html.escape(document_parts.page_title)
    if quirk_name == "without_boundary_tags":
        return "\n".join(
            [
                f"<title>{escaped_title}</title>",
                document_parts.head_markup,
                document_parts.head_filler,
                f'<div class="page" dir="{locale_entry.text_direction}">',
                document_parts.body_filler,
                "</div>",
            ]
        )
    head_closing_markup: typing.Final[str] = "" if quirk_name == "missing_head_closing_tag" else "</head>"
    return "\n".join(
        [
            "<!DOCTYPE html>",
            f'<html lang="{locale_entry.language_code}" dir="{locale_entry.text_direction}">',
            "<head>",
            document_parts.head_markup,
            f"<title>{escaped_title}</title>",
            document_parts.head_filler,
            head_closing_markup,
            f'<body class="page" dir="{locale_entry.text_direction}">',
            document_parts.body_markup,
            document_parts.body_filler,
            "</body>",
            "</html>",
        ]
    )


def _filter_effective_tags(planned_tags: list[PlannedMetaTag], *, include_body: bool) -> list[PlannedMetaTag]:
    return [
        one_meta_tag
        for one_meta_tag in planned_tags
        if (include_body or not one_meta_tag.placed_in_body)
        and not one_meta_tag.omit_content
        and one_meta_tag.content_value
    ]


def _build_expected_social_pairs(
    effective_tags: list[PlannedMetaTag],
    tag_prefix: str,
    *,
    allowed_kinds: tuple[str, ...],
) -> list[list[str]]:
    return [
        [one_meta_tag.attribute_value.lower().strip().removeprefix(tag_prefix), one_meta_tag.content_value]
        for one_meta_tag in effective_tags
        if one_meta_tag.attribute_kind in allowed_kinds
        and one_meta_tag.attribute_value.lower().strip().startswith(tag_prefix)
    ]


def _build_expected_basic_pairs(effective_tags: list[PlannedMetaTag]) -> list[list[str]]:
    collected_pairs: typing.Final[dict[str, str]] = {}
    for one_meta_tag in effective_tags:
        identifier_text: str = one_meta_tag.attribute_value.lower().strip()
        if one_meta_tag.attribute_kind != "name" or identifier_text not in BASIC_META_TAG_NAMES:
            continue
        collected_pairs.setdefault(identifier_text, one_meta_tag.content_value)
    return [[one_name, one_value] for one_name, one_value in collected_pairs.items()]


def _build_expected_other_pairs(effective_tags: list[PlannedMetaTag]) -> list[list[str]]:
    return [
        [one_meta_tag.attribute_value.lower().strip(), one_meta_tag.content_value]
        for one_meta_tag in effective_tags
        if one_meta_tag.attribute_kind == "name"
        and not one_meta_tag.attribute_value.lower().strip().startswith("twitter:")
        and one_meta_tag.attribute_value.lower().strip() not in BASIC_META_TAG_NAMES
    ]


def _parse_expected_dimension(dimension_text: str) -> int:
    cleaned_text: typing.Final[str] = dimension_text.strip()
    if not cleaned_text.isascii() or not cleaned_text.isdigit():
        return 0
    return int(cleaned_text)


def _build_expected_snippet(social_pairs: list[list[str]]) -> dict[str, typing.Any]:
    prepared_snippet: typing.Final[dict[str, typing.Any]] = {
        one_field_name: 0 if one_field_name in DIMENSION_FIELD_NAMES else "" for one_field_name in SNIPPET_FIELD_NAMES
    }
    already_filled: typing.Final[set[str]] = set()
    for one_tag_name, one_tag_value in social_pairs:
        snippet_field_name: str = one_tag_name.replace(":", "_")
        if snippet_field_name not in SNIPPET_FIELD_NAMES or snippet_field_name in already_filled:
            continue
        already_filled.add(snippet_field_name)
        prepared_snippet[snippet_field_name] = (
            _parse_expected_dimension(one_tag_value) if snippet_field_name in DIMENSION_FIELD_NAMES else one_tag_value
        )
    return prepared_snippet


def _build_expected_group(
    planned_tags: list[PlannedMetaTag],
    page_title: str,
    *,
    include_body: bool,
) -> dict[str, typing.Any]:
    effective_tags: typing.Final[list[PlannedMetaTag]] = _filter_effective_tags(planned_tags, include_body=include_body)
    open_graph_pairs: typing.Final[list[list[str]]] = _build_expected_social_pairs(
        effective_tags, "og:", allowed_kinds=("property",)
    )
    twitter_pairs: typing.Final[list[list[str]]] = _build_expected_social_pairs(
        effective_tags, "twitter:", allowed_kinds=("name", "property")
    )
    return {
        "title": page_title.strip(),
        "basic": _build_expected_basic_pairs(effective_tags),
        "open_graph": open_graph_pairs,
        "twitter": twitter_pairs,
        "other": _build_expected_other_pairs(effective_tags),
        "snippet_open_graph": _build_expected_snippet(open_graph_pairs),
        "snippet_twitter": _build_expected_snippet(twitter_pairs),
    }


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class RenderedPage:
    """One fully rendered page together with the plan it was rendered from."""

    page_text: str
    page_title: str
    planned_tags: tuple[PlannedMetaTag, ...]


def _render_planned_page(
    one_blueprint: PageBlueprint,
    locale_entry: corpus_locales.LocaleContent,
    *,
    encoding_name: str,
) -> RenderedPage:
    random_source: typing.Final[random.Random] = random.Random(f"{CORPUS_RANDOM_SEED}:{one_blueprint.page_slug}")
    markup_style: typing.Final[PageMarkupStyle] = _choose_markup_style(one_blueprint.quirk_name)
    page_title: typing.Final[str] = _choose_page_title(
        locale_entry, one_blueprint.quirk_name, random_source=random_source
    )
    planned_tags: typing.Final[list[PlannedMetaTag]] = _override_charset_declaration(
        [
            *ARCHETYPE_BUILDERS[one_blueprint.archetype_name](locale_entry, random_source),
            *_build_quirk_specific_tags(locale_entry, one_blueprint.quirk_name, random_source=random_source),
        ],
        encoding_name,
        quirk_name=one_blueprint.quirk_name,
    )
    document_parts: typing.Final[PageDocumentParts] = PageDocumentParts(
        page_title=page_title,
        head_markup="\n".join(
            _render_meta_tag(one_meta_tag, markup_style)
            for one_meta_tag in planned_tags
            if not one_meta_tag.placed_in_body
        ),
        body_markup="\n".join(
            _render_meta_tag(one_meta_tag, markup_style) for one_meta_tag in planned_tags if one_meta_tag.placed_in_body
        ),
        head_filler=_build_head_filler(locale_entry, random_source, filler_scale=one_blueprint.filler_scale),
        body_filler=_build_body_filler(locale_entry, random_source, filler_scale=one_blueprint.filler_scale),
    )
    return RenderedPage(
        page_text=_render_page_document(locale_entry, one_blueprint.quirk_name, document_parts=document_parts),
        page_title=page_title,
        planned_tags=tuple(planned_tags),
    )


def _convert_page_to_bytes(page_text: str, encoding_name: str) -> bytes | None:
    try:
        return page_text.encode(encoding_name)
    except UnicodeEncodeError:
        return None


def _build_one_page(one_blueprint: PageBlueprint) -> tuple[bytes, dict[str, typing.Any]]:
    locale_entry: typing.Final[corpus_locales.LocaleContent] = _choose_locale_entry(one_blueprint.locale_key)
    candidate_encoding: typing.Final[str] = _choose_encoding_name(locale_entry, one_blueprint)
    candidate_page: typing.Final[RenderedPage] = _render_planned_page(
        one_blueprint, locale_entry, encoding_name=candidate_encoding
    )
    candidate_bytes: typing.Final[bytes | None] = _convert_page_to_bytes(candidate_page.page_text, candidate_encoding)
    encoding_name: typing.Final[str] = candidate_encoding if candidate_bytes is not None else "utf-8"
    rendered_page: typing.Final[RenderedPage] = (
        candidate_page
        if candidate_bytes is not None
        else _render_planned_page(one_blueprint, locale_entry, encoding_name="utf-8")
    )
    raw_page_bytes: typing.Final[bytes] = (
        candidate_bytes if candidate_bytes is not None else rendered_page.page_text.encode("utf-8")
    )
    planned_tags: typing.Final[list[PlannedMetaTag]] = list(rendered_page.planned_tags)
    page_title: typing.Final[str] = rendered_page.page_title
    prefixed_page_bytes: typing.Final[bytes] = (
        b"\xef\xbb\xbf" + raw_page_bytes if one_blueprint.quirk_name == "byte_order_mark" else raw_page_bytes
    )
    return prefixed_page_bytes, {
        "slug": one_blueprint.page_slug,
        "file_name": f"{one_blueprint.page_slug}.html.gz",
        "language": locale_entry.language_code,
        "locale": locale_entry.locale_code,
        "text_direction": locale_entry.text_direction,
        "archetype": one_blueprint.archetype_name,
        "quirk": one_blueprint.quirk_name,
        "encoding": encoding_name,
        "raw_size_bytes": len(prefixed_page_bytes),
        "expected_default": _build_expected_group(planned_tags, page_title, include_body=False),
        "expected_full": _build_expected_group(planned_tags, page_title, include_body=True),
    }


def _build_all_blueprints() -> list[PageBlueprint]:
    all_combinations: typing.Final[list[tuple[str, str]]] = sorted(
        itertools.product(sorted(corpus_locales.ALL_LOCALES), ARCHETYPE_NAMES)
    )
    random.Random(CORPUS_RANDOM_SEED).shuffle(all_combinations)
    prepared_blueprints: typing.Final[list[PageBlueprint]] = []
    for page_index, one_combination in enumerate(all_combinations[:TOTAL_PAGES_COUNT]):
        locale_key, archetype_name = one_combination
        quirk_name: str = QUIRK_NAMES[page_index % len(QUIRK_NAMES)]
        page_slug: str = f"{page_index:03d}-{locale_key}-{archetype_name.replace('_', '-')}"
        filler_scale: int = (
            SMALL_FILLER_SCALE
            if quirk_name in ("without_boundary_tags", "very_long_content")
            else random.Random(page_slug).choice(FILLER_SCALE_STEPS)
        )
        prepared_blueprints.append(
            PageBlueprint(
                page_slug=page_slug,
                locale_key=locale_key,
                archetype_name=archetype_name,
                quirk_name=quirk_name,
                filler_scale=filler_scale,
                use_legacy_encoding=quirk_name == "legacy_encoding" or page_index % LEGACY_ENCODING_STRIDE == 1,
            )
        )
    return prepared_blueprints


def build_html_corpus() -> None:
    """Write every corpus page and the expectations manifest next to them."""
    CORPUS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for one_stale_file in CORPUS_DIRECTORY.glob("*.html.gz"):
        one_stale_file.unlink()
    collected_expectations: typing.Final[list[dict[str, typing.Any]]] = []
    for one_blueprint in _build_all_blueprints():
        page_bytes, page_expectations = _build_one_page(one_blueprint)
        CORPUS_DIRECTORY.joinpath(page_expectations["file_name"]).write_bytes(gzip.compress(page_bytes, mtime=0))
        collected_expectations.append(page_expectations)
    CORPUS_DIRECTORY.joinpath(EXPECTATIONS_FILE_NAME).write_text(
        json.dumps({"pages": collected_expectations}, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    build_html_corpus()
