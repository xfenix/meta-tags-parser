"""Test through public interfaces, e.g. main tests here."""
import pytest

from meta_tags_parser import parse_meta_tags_from_source, structs


@pytest.mark.parametrize("_", range(5))
def test_parse_from_random_memory(provide_fake_meta, _):
    """Random based tests of main parsing."""
    result: structs.TagsGroup = parse_meta_tags_from_source(provide_fake_meta[1])
    for one_group in (result.open_graph, result.twitter):
        for one_tag in one_group:
            assert one_tag.name in provide_fake_meta[0].keys()
    assert len(result.title) > 0
    assert len(result.other) == 2
