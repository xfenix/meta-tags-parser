import pathlib
import random
import typing

import pytest
from faker import Faker

from meta_tags_parser import structs


FIXTURES_DIR: typing.Final[pathlib.Path] = pathlib.Path(__file__).parent / "html_fixtures"
HTML_FIXTURES: typing.Final[tuple[str, ...]] = tuple(sorted(one_file.stem for one_file in FIXTURES_DIR.glob("*.html")))
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


def _build_tag_content(faker: Faker, one_name: str) -> str:
    if one_name in ("url", "video"):
        return faker.url()
    if one_name == "image":
        return faker.image_url()
    return faker.text()


@pytest.fixture
def provide_fake_meta(faker: Faker) -> tuple[dict[str, str], str]:
    """Generate random wannabe html tags."""
    output_buffer: typing.Final[list[str]] = []
    control_result: typing.Final[list[tuple[str, str]]] = []
    output_buffer.extend(
        f"""<meta name="{one_name}" content="{faker.text()}">""" for one_name in structs.BASIC_META_TAGS
    )
    for one_name in POSSIBLE_OG_TAGS_VALUES:
        for _ in range(random.randint(1, 5)):
            tag_content: str = _build_tag_content(faker, one_name)
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
