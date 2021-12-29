"""Fixtures basically."""
import random

from meta_tags_parser.parse import structs

import pytest


POSSIBLE_OG_TAGS_VALUES: tuple[str, ...] = (
    "title",
    "url",
    "image",
    "type",
    "description",
    "locale",
    "site_name",
    "video",
)


@pytest.fixture
def provide_fake_meta(faker):
    output_buffer: list = []
    control_result: list = []
    for one_name in structs.BASIC_META_TAGS:
        output_buffer.append(f"""<meta name="{one_name}" content="{faker.text()}">""")
    for one_name in POSSIBLE_OG_TAGS_VALUES:
        for _ in range(random.randint(1, 5)):
            tag_content: str
            if one_name in ("video", "image"):
                tag_content = faker.url()
            else:
                tag_content = faker.text()
            output_buffer.append(f"""<meta property="og:{one_name}" content="{tag_content}">""")
            output_buffer.append(f"""<meta name="twitter:{one_name}" content="{tag_content}">""")
            control_result.append((one_name, tag_content))
    output_buffer.append(f"<title>{faker.text()}</title>")
    return dict(control_result), ("\n \t" * random.randint(1, 5)).join(output_buffer)


__all__ = ["provide_fake_meta"]
