"""Fixtures basically."""
import pathlib
import random
import typing

import pytest

from meta_tags_parser.parse import structs


FIXTURES_DIR: typing.Final[pathlib.Path] = pathlib.Path(__file__).parent / "html_fixtures"
HTML_FIXTURES: typing.Final[tuple[str, ...]] = ("globo-com", "gazeta-ru")
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
    """Basic random wannabe html generator of raw tags."""
    output_buffer: list = []
    control_result: list = []
    for one_name in structs.BASIC_META_TAGS:
        output_buffer.append(f"""<meta name="{one_name}" content="{faker.text()}">""")
    for one_name in POSSIBLE_OG_TAGS_VALUES:
        for _ in range(random.randint(1, 5)):
            tag_content: str
            if one_name in ("url", "video"):
                tag_content = faker.url()
            elif one_name == "image":
                tag_content = faker.image_url()
            else:
                tag_content = faker.text()
            output_buffer.append(f"""<meta property="og:{one_name}" content="{tag_content}">""")
            output_buffer.append(f"""<meta name="twitter:{one_name}" content="{tag_content}">""")
            control_result.append((one_name, tag_content))
    output_buffer.append(f"<title>{faker.text()}</title>")
    output_buffer.append(f"""<meta name="article:{faker.name()}" content="{faker.text()}">""")
    return dict(control_result), ("\n \t" * random.randint(1, 5)).join(output_buffer)


@pytest.fixture
def provide_html_file_paths():
    """File paths for raw parse test."""
    return [FIXTURES_DIR.joinpath(f"{one_name}.html") for one_name in HTML_FIXTURES]


__all__ = ["provide_fake_meta"]
