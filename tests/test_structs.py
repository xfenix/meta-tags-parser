import dataclasses

import pytest

from meta_tags_parser import structs


@pytest.mark.parametrize(
    ("tested_instance", "target_field_name", "new_value"),
    [
        (structs.OneMetaTag(name="a", value="b"), "name", "c"),
        (structs.ValuesGroup(original="d", normalized="e"), "original", "f"),
        (structs.TagsGroup(), "title", "g"),
        (
            structs.SnippetGroup(),
            "twitter",
            structs.SocialMediaSnippet(title="h"),
        ),
        (structs.SocialMediaSnippet(), "title", "i"),
    ],
)
def test_structs_are_frozen(
    tested_instance: object,
    target_field_name: str,
    new_value: object,
) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(tested_instance, target_field_name, new_value)
