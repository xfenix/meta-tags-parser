import json
import types
import typing
import xml.etree.ElementTree as ET
from pathlib import Path


COVERAGE_XML_PATH: typing.Final = Path("coverage.xml")
BADGE_JSON_PATH: typing.Final = Path(".github/badges/coverage.json")
LOW_BOUNDARY: typing.Final[float] = 60
HIGH_BOUNDARY: typing.Final[float] = 80


def build_badge_file() -> None:
    xml_source_text: typing.Final[str] = COVERAGE_XML_PATH.read_text()
    root_element: typing.Final[ET.Element] = ET.fromstring(xml_source_text)  # noqa: S314
    line_rate_text: typing.Final[str] = root_element.attrib["line-rate"]
    coverage_percent: typing.Final[float] = float(line_rate_text) * 100.0

    message_text: typing.Final[str] = f"{coverage_percent:.0f}%"
    color_text: str
    if coverage_percent < LOW_BOUNDARY:
        color_text = "#E63946"
    elif coverage_percent < HIGH_BOUNDARY:
        color_text = "#FFB347"
    else:
        color_text = "#2A9D8F"

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
