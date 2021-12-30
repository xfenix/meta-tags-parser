"""Test through public interfaces, e.g. main tests here."""
from meta_tags_parser import parse_meta_tags_from_source, structs

import pytest


@pytest.mark.parametrize("_", range(5))
def test_parse_from_memory(provide_fake_meta, _):
    """Random based tests of main parsing."""
    result: structs.TagsGroup = parse_meta_tags_from_source(provide_fake_meta[1])
    for one_tag in result.og:
        assert one_tag.name in provide_fake_meta[0].keys()
        print(one_tag)
        # assert one_tag.value not in provide_fake_meta[0].values()


def test_parse_from_file(provide_html_file_paths):
    """File based static tests of main parsing."""
    for one_file in provide_html_file_paths:
        parse_meta_tags_from_source(one_file.read_text())


__all__ = ["test_parse_from_file", "test_parse_from_memory"]
