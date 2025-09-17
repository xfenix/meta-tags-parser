import hypothesis
import hypothesis.strategies as st

from meta_tags_parser.parse import _slice_html_for_meta
from meta_tags_parser.structs import SettingsFromUser


@hypothesis.given(st.text(alphabet=st.characters(blacklist_characters='<>"'), min_size=1, max_size=100))
def test_slice_html_stops_at_head_end(description: str) -> None:
    html_source: str = f'<html><head><meta name="description" content="{description}"></head><body>ignored'
    sliced_html: str = _slice_html_for_meta(html_source, active_options=SettingsFromUser())
    assert sliced_html.endswith("</head>")
    assert "<body" not in sliced_html


@hypothesis.given(st.text(min_size=200))
def test_slice_html_without_boundary(prefix_text: str) -> None:
    html_source: str = "<html>" + prefix_text
    expected_length: int = 50
    sliced_html: str = _slice_html_for_meta(
        html_source,
        active_options=SettingsFromUser(fallback_limit_chars=expected_length, max_scan_chars=200),
    )
    assert len(sliced_html) == expected_length
