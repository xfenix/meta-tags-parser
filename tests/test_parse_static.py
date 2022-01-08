"""Test through public interfaces, e.g. main tests here."""
from meta_tags_parser import parse_meta_tags_from_source, parse_snippets_from_source, structs


_STATIC_FIXTURE_1: str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://metatags.io/">
    <meta property="og:title" content="Meta Tags — Preview, Edit and Generate">
    <meta property="og:description" content="With Meta Tags you can edit and experiment with your content then preview how your webpage will look on Google, Facebook, Twitter and more!">
    <meta property="og:image" content="https://metatags.io/assets/meta-tags-16a33a6a8531e519cc0936fbba0ad904e52d35f34a46c97a2c9f6f7dd7d336f2.png">
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://metatags.io/">
    <meta property="twitter:title" content="Privet, kak dela to vcelom?">
    <meta property="twitter:description" content="With Meta Tags you can edit and experiment with your content then preview how your webpage will look on Google, Facebook, Twitter and more!">
    <meta property="twitter:image" content="https://metatags.io/assets/hm-fail.png">
</head>
<body>
    <a href="#">Kek</a>
</body>
</html>
"""


def test_parse_from_file(provide_html_file_paths):
    """File based static tests of main parsing."""
    for one_file in provide_html_file_paths:
        parse_meta_tags_from_source(one_file.read_text())


def test_parse_good_static():
    """Static based test but with more good asserts."""
    positive_result: structs.TagsGroup = parse_meta_tags_from_source(_STATIC_FIXTURE_1)

    assert structs.OneMetaTag(name="type", value="website") in positive_result.open_graph
    assert (
        structs.OneMetaTag(name="title", value="Meta Tags — Preview, Edit and Generate") in positive_result.open_graph
    )
    assert (
        structs.OneMetaTag(
            name="image",
            value="https://metatags.io/assets/meta-tags-16a33a6a8531e519cc0936fbba0ad904e52d35f34a46c97a2c9f6f7dd7d336f2.png",
        )
        in positive_result.open_graph
    )
    assert structs.OneMetaTag(name="card", value="summary_large_image") in positive_result.twitter
    assert structs.OneMetaTag(name="title", value="Privet, kak dela to vcelom?") in positive_result.twitter


def test_snippet_parsing_static():
    """Test snippet parsing."""
    assert parse_snippets_from_source(_STATIC_FIXTURE_1) == structs.SnippetGroup(
        open_graph=structs.SocialMediaSnippet(
            title="Meta Tags — Preview, Edit and Generate",
            description="With Meta Tags you can edit and experiment with your content then preview how your webpage will look on Google, Facebook, Twitter and more!",
            image="https://metatags.io/assets/meta-tags-16a33a6a8531e519cc0936fbba0ad904e52d35f34a46c97a2c9f6f7dd7d336f2.png",
            url="https://metatags.io/",
        ),
        twitter=structs.SocialMediaSnippet(
            title="Privet, kak dela to vcelom?",
            description="With Meta Tags you can edit and experiment with your content then preview how your webpage will look on Google, Facebook, Twitter and more!",
            image="https://metatags.io/assets/hm-fail.png",
            url="https://metatags.io/",
        ),
    )
