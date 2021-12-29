"""Test through public interfaces, e.g. main tests here."""
from meta_tags_parser import parse_meta_tags_from_source, structs

import pytest


@pytest.mark.parametrize("_", range(5))
def test_parse_from_file(provide_fake_meta, _):
    result: structs.TagsGroup = parse_meta_tags_from_source(provide_fake_meta[1])
    for one_tag in result.og:
        if one_tag.name not in provide_fake_meta[0].keys() or one_tag.value not in provide_fake_meta[0].values():
            raise AssertionError(f"Not parsed {one_tag}")


__all__ = ["test_parse_from_file"]
