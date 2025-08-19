from meta_tags_parser import parse_meta_tags_from_source, structs


def test_parse_handles_malformed_html() -> None:
    html_source = """
    <html><head>
    <meta name="description" content="Valid description">
    <meta property="og:title" content="OG Title">
    <meta name="keywords" content="foo,bar"
    </head></html>
    """
    parse_result = parse_meta_tags_from_source(html_source)
    assert structs.OneMetaTag(name="description", value="Valid description") in parse_result.basic
    assert structs.OneMetaTag(name="title", value="OG Title") in parse_result.open_graph


def test_attribute_normalization_in_parser() -> None:
    html_source = """
    <meta PROPERTY="OG:TITLE" CONTENT="HELLO">
    <meta NAME="TWITTER:DESCRIPTION" CONTENT="WORLD">
    """
    parse_result = parse_meta_tags_from_source(html_source)
    assert structs.OneMetaTag(name="title", value="HELLO") in parse_result.open_graph
    assert structs.OneMetaTag(name="description", value="WORLD") in parse_result.twitter
