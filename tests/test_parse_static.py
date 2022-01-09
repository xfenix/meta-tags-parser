"""Test through public interfaces, e.g. main tests here."""
from ._fixtures import FIXTURE_ONE
from meta_tags_parser import parse_meta_tags_from_source, parse_snippets_from_source, structs


def test_parse_from_file(
    provide_html_file_paths,
):
    """File based static tests of main parsing."""
    for one_file in provide_html_file_paths:
        parse_meta_tags_from_source(one_file.read_text())


def test_parse_good_static():
    """Static based test but with more good asserts."""
    positive_result: structs.TagsGroup = parse_meta_tags_from_source(FIXTURE_ONE)

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


def test_snippet_parsing_static():
    """Test snippet parsing."""
    snippet_obj: structs.SnippetGroup = parse_snippets_from_source(FIXTURE_ONE)
    assert snippet_obj == structs.SnippetGroup(
        open_graph=structs.SocialMediaSnippet(
            title="Meta Tags — Preview, Edit and Generate",
            description=(
                (
                    "With Meta Tags you can edit and\n"
                    "    experiment with your content then preview how your webpage will look on Google, "
                    "Facebook, Twitter and more!"
                )
            ),
            image=(
                "https://metatags.io/assets/meta-tags-16a33a6a853"
                "1e519cc0936fbba0ad904e52d35f34a46c97a2c9f6f7dd7d336f2.png"
            ),
            url="https://metatags.io/",
        ),
        twitter=structs.SocialMediaSnippet(
            title="Privet, kak dela to vcelom?",
            description=(
                (
                    "With Meta Tags you can edit and experiment with your content then preview\n"
                    "    how your webpage will look on Google, Facebook, Twitter and more!"
                )
            ),
            image="https://metatags.io/assets/hm-fail.png",
            url="https://metatags.io/",
        ),
    ), snippet_obj
