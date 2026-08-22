import dataclasses
import pathlib
import typing

import hypothesis
import pytest
from faker import Faker

from meta_tags_parser import parse, structs


FIXTURES_DIRECTORY: typing.Final = pathlib.Path(__file__).parent / "html_fixtures"
DETERMINISTIC_SEED: typing.Final = 20260818
HYPOTHESIS_PROFILE_NAME: typing.Final = "meta-tags-parser"
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
EXTRA_OTHER_TAG_NAMES: typing.Final[tuple[str, ...]] = ("article:name", "article:description")
REPEATED_TAG_LIMIT: typing.Final = 5


# parsing multi megabyte fixtures is slower than the hypothesis default deadline allows,
# and a deadline makes property tests flaky on loaded CI runners
hypothesis.settings.register_profile(HYPOTHESIS_PROFILE_NAME, deadline=None, print_blob=True)
hypothesis.settings.load_profile(HYPOTHESIS_PROFILE_NAME)


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class FakeMetaPage:
    """Randomly generated page together with what the parser must find inside it."""

    html_source: str
    social_tag_values: typing.Mapping[str, str]
    other_tag_names: tuple[str, ...]


@pytest.fixture(name="faker_seed", autouse=True)
def provide_faker_seed() -> int:
    """Keep faker output reproducible, a failing test must be replayable."""
    return DETERMINISTIC_SEED


@pytest.fixture(autouse=True)
def restore_global_settings() -> typing.Iterator[None]:
    """Undo whatever set_settings_for_meta_tags did inside a test."""
    yield
    parse.set_settings_for_meta_tags(structs.DEFAULT_SETTINGS_FROM_USER)


def _build_tag_content(faker: Faker, one_name: str) -> str:
    if one_name in ("url", "video"):
        return str(faker.url())
    if one_name == "image":
        return str(faker.image_url())
    return str(faker.text())


@pytest.fixture
def provide_fake_meta_page(faker: Faker) -> FakeMetaPage:
    """Generate a random page with known Open Graph, Twitter, basic and other tags."""
    markup_buffer: typing.Final[list[str]] = [
        f"""<meta name="{one_name}" content="{faker.text()}">""" for one_name in structs.BASIC_META_TAGS
    ]
    social_tag_values: typing.Final[dict[str, str]] = {}
    for one_name in POSSIBLE_OG_TAGS_VALUES:
        for _ in range(faker.random_int(min=1, max=REPEATED_TAG_LIMIT)):
            tag_content: str = _build_tag_content(faker, one_name)
            markup_buffer.append(f"""<meta property="og:{one_name}" content="{tag_content}">""")
            markup_buffer.append(f"""<meta name="twitter:{one_name}" content="{tag_content}">""")
            social_tag_values[one_name] = tag_content
    markup_buffer.append(f"<title>{faker.text()}</title>")
    markup_buffer.extend(f"""<meta name="{one_name}" content="{faker.text()}">""" for one_name in EXTRA_OTHER_TAG_NAMES)
    markup_buffer.append("""<meta name="bad-tag">""")
    markup_buffer.append("""<meta property="another-bad-tag">""")
    return FakeMetaPage(
        html_source=("\n \t" * faker.random_int(min=1, max=REPEATED_TAG_LIMIT)).join(markup_buffer),
        social_tag_values=social_tag_values,
        other_tag_names=EXTRA_OTHER_TAG_NAMES,
    )


@pytest.fixture
def provide_html_file_paths() -> list[pathlib.Path]:
    """Return the real captured pages shipped with the repository."""
    return sorted(FIXTURES_DIRECTORY.glob("*.html"))
