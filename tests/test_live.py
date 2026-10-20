"""Checks against the real netztransparenz.de page. Skipped unless pytest runs with --live."""

from __future__ import annotations

import pytest

from eeg_bewegungsdaten.links import UENB, find_links


@pytest.mark.live
def test_page_lists_all_four_tsos_for_the_newest_year() -> None:
    links = find_links(older=False)

    data = [link for link in links if link.kind == "bewegungsdaten"]
    newest = max(link.year for link in data if link.year is not None)
    assert sorted(str(link.uenb) for link in data if link.year == newest) == sorted(UENB)
    assert all(link.file_id for link in data)
    assert any(link.kind == "legende" for link in links)
