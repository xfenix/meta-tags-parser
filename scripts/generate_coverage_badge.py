import json
import types
import typing
import xml.etree.ElementTree as ET
from pathlib import Path


COVERAGE_XML_PATH: typing.Final = Path("coverage.xml")
BADGE_JSON_PATH: typing.Final = Path(".github/badges/coverage.json")
LOW_BOUNDARY: typing.Final = 60.0
HIGH_BOUNDARY: typing.Final = 80.0


def _choose_badge_color(coverage_percent: float) -> str:
    if coverage_percent < LOW_BOUNDARY:
        return "#E63946"
    if coverage_percent < HIGH_BOUNDARY:
        return "#FFB347"
    return "#2A9D8F"


def build_badge_file() -> None:
    coverage_percent: typing.Final[float] = (
        float(ET.fromstring(COVERAGE_XML_PATH.read_text()).attrib["line-rate"]) * 100.0  # noqa: S314
    )

    message_text: typing.Final[str] = f"{coverage_percent:.0f}%"
    color_text: typing.Final[str] = _choose_badge_color(coverage_percent)

    badge_mapping: typing.Final[typing.Mapping[str, typing.Any]] = types.MappingProxyType(
        {
            "schemaVersion": 1,
            "label": "coverage",
            "message": message_text,
            "color": color_text,
        },
    )

    BADGE_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    BADGE_JSON_PATH.write_text(json.dumps(dict(badge_mapping)))


if __name__ == "__main__":
    build_badge_file()
