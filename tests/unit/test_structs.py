import dataclasses
import typing

import pytest

from meta_tags_parser import structs
from tests import factories


GENERATED_TAGS_COUNT: typing.Final = 25


@pytest.mark.parametrize(
    ("tested_instance", "target_field_name", "new_value"),
    [
        (structs.OneMetaTag(name="title", value="hello"), "name", "description"),
        (structs.ValuesGroup(original="Value", normalized="value"), "original", "other"),
        (structs.TagsGroup(), "title", "page title"),
        (structs.SnippetGroup(), "twitter", structs.SocialMediaSnippet(title="snippet")),
        (structs.SocialMediaSnippet(), "title", "snippet title"),
        (structs.SettingsFromUser(), "optimize_input", False),
    ],
)
def test_structs_are_frozen(tested_instance: object, target_field_name: str, new_value: object) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(tested_instance, target_field_name, new_value)


@pytest.mark.parametrize(
    ("original_name", "expected_normalized_name"),
    [
        ("title", "title"),
        ("image:width", "image_width"),
        ("image:secure_url", "image_secure_url"),
        ("", ""),
    ],
)
def test_normalized_name_replaces_colons(original_name: str, expected_normalized_name: str) -> None:
    assert structs.OneMetaTag(name=original_name, value="x").normalized_name == expected_normalized_name


def test_tag_name_cache_is_bounded() -> None:
    """Tag names come from arbitrary pages, an unbounded cache would grow without limit."""
    assert structs._transform_tag_name.cache_info().maxsize == structs.TAG_NAME_CACHE_SIZE


def test_snippet_dimension_fields_exist_on_the_snippet_struct() -> None:
    assert structs.DIMENSION_SNIPPET_FIELDS.issubset(structs.WHAT_ATTRS_IN_SOCIAL_MEDIA_SNIPPET)


def test_default_settings_parse_everything() -> None:
    assert set(structs.DEFAULT_SETTINGS_FROM_USER.what_to_parse) == set(structs.WhatToParse)
    assert structs.DEFAULT_SETTINGS_FROM_USER.optimize_input is True


@pytest.mark.parametrize("generated_tag", factories.OneMetaTagFactory.batch(GENERATED_TAGS_COUNT))
def test_normalized_name_never_contains_colons(generated_tag: structs.OneMetaTag) -> None:
    assert ":" not in generated_tag.normalized_name
    assert generated_tag.normalized_name == generated_tag.name.replace(":", "_")
