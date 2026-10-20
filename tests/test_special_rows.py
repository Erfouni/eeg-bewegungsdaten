"""The marks in `sonderzeile` and the filters built on them, with categories from 2016 to 2025."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from eeg_bewegungsdaten import generation, grid_feed_in
from eeg_bewegungsdaten.special_rows import special_row
from tests.builders import read_lines, row


@pytest.mark.parametrize(
    ("category", "code"),
    [
        ("BiK54G-----FLP", "REPEATED_ENERGY"),
        ("BiK54M-----FLP", "REPEATED_ENERGY"),
        ("SgK33a2-----SV", "SELF_CONSUMPTION"),
        ("BiK33a2-----SV", "SELF_CONSUMPTION"),
        ("SgK3341-----09", "PAID_SELF_CONSUMPTION"),
        ("SgK33410----12", "PAID_SELF_CONSUMPTION"),
        ("SgK3342-----09", "SELF_CONSUMPTION_DEDUCTION"),
        ("SgK33420----12", "SELF_CONSUMPTION_DEDUCTION"),
        ("SgK3343-----10", "SELF_CONSUMPTION_DEDUCTION"),
        ("BiK23b1----aMW", "ENDED_SUPPORT"),
        ("SgK334-----aMW", "ENDED_SUPPORT"),
        ("BiK33b3--SO-DV", "OTHER_DIRECT_MARKETING"),
        # "SV" inside the category: no rule yet, see "Special rows" in docs/findings.md
        ("SgK-kVG--SV--0", None),
        ("SgK334-SV----0", None),
        ("SgK4820--Feb24", None),
        (None, None),
    ],
)
def test_category_gets_its_code(category: str | None, code: str | None) -> None:
    frame = pl.DataFrame({"verguetungskategorie": [category]}, schema={"verguetungskategorie": str})

    marked = frame.select(special_row(pl.col("verguetungskategorie")))

    assert marked.item() == code


def test_clean_rows_carry_the_code(tmp_path: Path) -> None:
    clean, _ = read_lines(
        tmp_path,
        row(category="BiK54G-----FLP", form="5", payment="0"),
        row(category="SgK4820--Feb24"),
    )

    assert clean["sonderzeile"].to_list() == ["REPEATED_ENERGY", None]


ROWS = pl.DataFrame(
    {
        "sonderzeile": [
            None,
            "REPEATED_ENERGY",
            "SELF_CONSUMPTION",
            "PAID_SELF_CONSUMPTION",
            "SELF_CONSUMPTION_DEDUCTION",
            "ENDED_SUPPORT",
            "OTHER_DIRECT_MARKETING",
        ],
        "strommenge": [100.0, 40.0, 7.0, 5.0, -5.0, 3.0, 20.0],
    }
)


def test_grid_feed_in_leaves_out_repeated_energy_and_self_consumption() -> None:
    assert ROWS.filter(grid_feed_in())["strommenge"].sum() == 100 + 3 + 20


def test_generation_keeps_self_consumption_but_not_its_deduction() -> None:
    assert ROWS.filter(generation())["strommenge"].sum() == 100 + 7 + 5 + 3 + 20
