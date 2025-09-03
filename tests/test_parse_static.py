import pathlib
import typing

from meta_tags_parser import parse_meta_tags_from_source, parse_snippets_from_source, structs


EXPECTED_TWITTER_TAGS_COUNT: typing.Final = 4


class TestCaseWithMultilineTags:
    """Basic cases with static multiline fixture."""

    FIXTURE_FOR_CASE: str = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        <!-- Open Graph / Facebook -->
        <meta name="single-tag-without-content">
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://metatags.io/">
        <meta property="og:title" content="Meta Tags — Preview, Edit and Generate">
        <meta property="og:description" content="With Meta Tags you can edit and
        experiment with your content then preview how your webpage will look on Google, Facebook, Twitter and more!">
        <meta property="og:image"
        content="https://metatags.io/assets/meta-tags-16a33a6a8531e519cc0936fbba0ad904e52d35f34a46c97a2c9f6f7dd7d336f2.png">
        <meta property="og:image:width" content="1200">
        <meta property="og:image:height" content="630">
        <!-- Twitter -->
        <meta property="twitter:card" content="summary_large_image">
        <meta property="twitter:url" content="https://metatags.io/">
        <meta property="twitter:title" content="Privet, kak dela to vcelom?">
        <meta property="twitter:description"
        content="With Meta Tags you can edit and experiment with your content then preview
        how your webpage will look on Google, Facebook, Twitter and more!">
        <meta property="twitter:image" content="https://metatags.io/assets/hm-fail.png">
        <meta property="twitter:image:width" content="1200">
        <meta property="twitter:image:height" content="630">
    </head>
    <body>
        <a href="#">Kek</a>
    </body>
    </html>
    """

    def test_parse_good_static(self) -> None:
        """Parse static content with more asserts."""
        positive_result: structs.TagsGroup = parse_meta_tags_from_source(self.FIXTURE_FOR_CASE)

        assert (
            structs.OneMetaTag(
                name="type",
                value="website",
            )
            in positive_result.open_graph
        )
        assert (
            structs.OneMetaTag(
                name="title",
                value="Meta Tags — Preview, Edit and Generate",
            )
            in positive_result.open_graph
        )
        assert (
            structs.OneMetaTag(
                name="image",
                value=(
                    "https://metatags.io/assets/meta-tags-16a33a6a8531e5"
                    "19cc0936fbba0ad904e52d35f34a46c97a2c9f6f7dd7d336f2.png"
                ),
            )
            in positive_result.open_graph
        )
        assert (
            structs.OneMetaTag(
                name="card",
                value="summary_large_image",
            )
            in positive_result.twitter
        )
        assert (
            structs.OneMetaTag(
                name="title",
                value="Privet, kak dela to vcelom?",
            )
            in positive_result.twitter
        )

    def test_snippet_parsing_static(self) -> None:
        """Test snippet parsing."""
        testable_object: structs.SnippetGroup
        good_result: structs.SnippetGroup = structs.SnippetGroup(
            open_graph=structs.SocialMediaSnippet(
                title="Meta Tags — Preview, Edit and Generate",
                description=(
                    "With Meta Tags you can edit and\n"
                    "        experiment with your content then preview how your webpage will look on Google, "
                    "Facebook, Twitter and more!"
                ),
                image=(
                    "https://metatags.io/assets/meta-tags-16a33a6a853"
                    "1e519cc0936fbba0ad904e52d35f34a46c97a2c9f6f7dd7d336f2.png"
                ),
                image_width=1200,
                image_height=630,
                url="https://metatags.io/",
            ),
            twitter=structs.SocialMediaSnippet(
                title="Privet, kak dela to vcelom?",
                description=(
                    "With Meta Tags you can edit and experiment with your content then preview\n"
                    "        how your webpage will look on Google, Facebook, Twitter and more!"
                ),
                image="https://metatags.io/assets/hm-fail.png",
                image_width=1200,
                image_height=630,
                url="https://metatags.io/",
            ),
        )
        # need parse multiple times in one session
        for _ in range(3):
            testable_object = parse_snippets_from_source(self.FIXTURE_FOR_CASE)
            assert testable_object == good_result, testable_object

        # fresh new "html"
        testable_object = parse_snippets_from_source("""<meta name="twitter:title" content="Hi, whatsup kekeke">""")
        assert testable_object.twitter.title == "Hi, whatsup kekeke"
        assert testable_object.open_graph.title == ""
        assert testable_object.open_graph.description == ""
        assert testable_object.twitter.image_width == 0
        assert testable_object.twitter.image_height == 0


def test_general_with_file_fixtures(
    provide_html_file_paths: list[pathlib.Path],
) -> None:
    """Parse meta tags from file fixtures."""
    for one_file in provide_html_file_paths:
        parse_result: structs.TagsGroup = parse_meta_tags_from_source(one_file.read_text())
        assert len(parse_result.open_graph) > 0
        assert len(parse_result.title) > 0


def test_parsing_any_twitter_tag() -> None:
    """Test case with name and property attrs for twitter."""
    example_fixture_with_name: str = """
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="https://github.com/">
    <meta name="twitter:title" content="Hello, my friend">
    <meta name="twitter:description" content="Content here, yehehe">
    """
    example_fixture_with_property: str = """
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://github.com/">
    <meta property="twitter:title" content="Hello, my friend">
    <meta property="twitter:description" content="Content here, yehehe">
    """
    for one_fixture in (example_fixture_with_name, example_fixture_with_property):
        parse_result: structs.TagsGroup = parse_meta_tags_from_source(one_fixture)
        assert len(parse_result.twitter) == EXPECTED_TWITTER_TAGS_COUNT
