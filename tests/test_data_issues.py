"""The yearly issues of .github/scripts/data_issues.py, planned from the fixture page."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType

from eeg_bewegungsdaten.links import newest_known_year, parse_links
from tests.builders import PAGE

SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "data_issues.py"
OCTOBER = dt.date(2026, 10, 18)


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("data_issues", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # dataclasses look the module up by name
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


issues = load()


def test_known_page_needs_no_issue() -> None:
    assert issues.plan(parse_links(PAGE), OCTOBER) == []


def test_new_year_opens_one_issue_per_task() -> None:
    year = newest_known_year() + 1
    page = PAGE.replace("bewegungsdaten%202025.zip", f"bewegungsdaten%20{year}.zip")

    planned = issues.plan(parse_links(page), dt.date(year + 1, 9, 5))

    assert [issue.title for issue in planned] == [
        f"Data {year}: read the files of 50Hertz",
        f"Data {year}: read the files of Amprion",
        f"Data {year}: read the files of TenneT",
        f"Data {year}: read the files of TransnetBW",
        f"Data {year}: keep the files for after they leave the page",
        f"Data {year}: compare with the EEG annual account",
        f"Data {year}: match with the MaStR",
        f"Data {year}: release a version that reads {year}",
    ]
    assert {issue.label for issue in planned} == {f"data {year}"}
    assert f"bewegungsdaten%20{year}.zip" in planned[1].body
    assert "--uenb amprion" in planned[1].body


def test_new_upload_of_a_known_year_opens_one_issue() -> None:
    page = PAGE.replace(
        "ff4ee575-7857-431e-f919-08def218fc48", "ff4ee575-0000-0000-0000-000000000000"
    )

    planned = issues.plan(parse_links(page), OCTOBER)

    assert [issue.title for issue in planned] == [
        "Data 2025: new upload of the TenneT 2025 file (2026-09-05)"
    ]
    assert "ff4ee575-0000-0000-0000-000000000000" in planned[0].body


def test_new_legend_opens_one_issue() -> None:
    page = PAGE.replace(
        "9d2cf962-999e-4810-29d3-08defc51206b", "9d2cf962-0000-0000-0000-000000000000"
    )

    planned = issues.plan(parse_links(page), OCTOBER)

    assert [issue.title for issue in planned] == [
        "Data 2025: new upload of the legend file (2026-09-04)"
    ]


def test_missing_year_after_15_september_opens_one_issue() -> None:
    page = parse_links(PAGE)

    assert issues.plan(page, dt.date(2027, 9, 15)) == []
    planned = issues.plan(page, dt.date(2027, 9, 16))

    assert [issue.title for issue in planned] == [
        "Data 2026: not on the page after 15 September 2027"
    ]


class FakeGh:
    def __init__(self, titles: Sequence[str]) -> None:
        self.titles = titles
        self.calls: list[tuple[list[str], str | None]] = []

    def __call__(self, args: Sequence[str], stdin: str | None) -> str:
        self.calls.append((list(args), stdin))
        if args[:2] == ["issue", "list"]:
            return json.dumps([{"title": title} for title in self.titles])
        return ""


def test_open_issues_skips_existing_titles_and_labels_the_rest() -> None:
    planned = [
        issues.Issue("Data 2026: one", "body one", 2026),
        issues.Issue("Data 2026: two", "body two", 2026),
    ]
    gh = FakeGh(["Data 2026: one"])

    opened = issues.open_issues(planned, gh)

    assert [issue.title for issue in opened] == ["Data 2026: two"]
    created = [(args, stdin) for args, stdin in gh.calls if args[:2] == ["issue", "create"]]
    assert created == [
        (
            [
                "issue",
                "create",
                "--title",
                "Data 2026: two",
                "--label",
                "data 2026",
                "--body-file",
                "-",
            ],
            "body two",
        )
    ]
    assert ["label", "create", "data 2026", "--color", "1d76db", "--force"] in [
        args for args, _ in gh.calls
    ]
