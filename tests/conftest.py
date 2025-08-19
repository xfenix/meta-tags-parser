from __future__ import annotations
import pathlib
import random
import typing

import pytest

from meta_tags_parser import settings


if typing.TYPE_CHECKING:
    from faker import Faker


FIXTURES_DIR: typing.Final[pathlib.Path] = pathlib.Path(__file__).parent / "html_fixtures"
HTML_FIXTURES: typing.Final[tuple[str, ...]] = ("globo-com", "gazeta-ru")
POSSIBLE_OG_TAGS_VALUES: typing.Final[tuple[str, ...]] = (
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
def provide_fake_meta(faker: Faker) -> tuple[dict[str, str], str]:
    """Generate random wannabe html tags."""
    output_buffer: list[str] = []
    control_result: list[tuple[str, str]] = []
    output_buffer.extend(
        f"""<meta name="{one_name}" content="{faker.text()}">""" for one_name in settings.BASIC_META_TAGS
    )
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
    output_buffer.append(f"""<meta name="article:name" content="{faker.text()}">""")
    output_buffer.append(f"""<meta name="article:description" content="{faker.text()}">""")
    output_buffer.append("""<meta name="bad-tag">""")
    output_buffer.append("""<meta property="another-bad-tag">""")
    return dict(control_result), ("\n \t" * random.randint(1, 5)).join(output_buffer)


@pytest.fixture
def provide_html_file_paths() -> list[pathlib.Path]:
    """Return file paths for raw parse test."""
    return [FIXTURES_DIR.joinpath(f"{one_name}.html") for one_name in HTML_FIXTURES]
