"""Where downloaded and generated files live, and how they are written."""

from __future__ import annotations

import datetime as dt
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

ENV_VAR = "EEG_BEWEGUNGSDATEN_DIR"


class Outputs(NamedTuple):
    """The files that `ingest` and `mastr` write for one year and TSO."""

    text: Path
    clean: Path
    quarantine: Path
    report: Path
    mastr: Path
    mastr_report: Path


def default_data_dir() -> Path:
    """`$EEG_BEWEGUNGSDATEN_DIR`, or `~/.eeg-bewegungsdaten`."""
    configured = os.environ.get(ENV_VAR)
    return Path(configured).expanduser() if configured else Path.home() / ".eeg-bewegungsdaten"


def raw_dir(data_dir: Path) -> Path:
    """Archive of the original files, one folder per upload."""
    return data_dir / "raw"


def text_dir(data_dir: Path) -> Path:
    """Every line with all fields as text, ``text/<year>/<tso>.parquet``."""
    return data_dir / "text"


def clean_dir(data_dir: Path) -> Path:
    """Parquet files in the common schema, ``clean/<year>/<tso>.parquet``."""
    return data_dir / "clean"


def quarantine_dir(data_dir: Path) -> Path:
    """Lines that could not be read, ``quarantine/<year>/<tso>.parquet``."""
    return data_dir / "quarantine"


def mastr_dir(data_dir: Path) -> Path:
    """Match of every clean row to the MaStR, ``mastr/<year>/<tso>.parquet``."""
    return data_dir / "mastr"


def reports_dir(data_dir: Path) -> Path:
    """Row counts and quality codes per file, ``reports/<year>/<tso>.json``."""
    return data_dir / "reports"


def export_dir(data_dir: Path) -> Path:
    """Dataset to share, ``export/eeg-bewegungsdaten-<year>.parquet`` and the source notes."""
    return data_dir / "export"


def anlage_id_path(data_dir: Path) -> Path:
    """Random id per TSO and Anlagenschluessel. It leads from the export back to the
    Anlagenschluessel, so it stays outside `export_dir`."""
    return data_dir / "anlage_id.parquet"


def output_paths(data_dir: Path, jahr: int, uenb: str) -> Outputs:
    name = f"{jahr}/{uenb}"
    return Outputs(
        text=text_dir(data_dir) / f"{name}.parquet",
        clean=clean_dir(data_dir) / f"{name}.parquet",
        quarantine=quarantine_dir(data_dir) / f"{name}.parquet",
        report=reports_dir(data_dir) / f"{name}.json",
        mastr=mastr_dir(data_dir) / f"{name}.parquet",
        mastr_report=reports_dir(data_dir) / f"{name}.mastr.json",
    )


def write_atomic(path: Path, write: Callable[[Path], object]) -> None:
    """Let `write` fill a temporary file next to `path`, then rename it, so that an aborted run
    never leaves half a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        write(tmp)
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def write_text(path: Path, text: str) -> None:
    write_atomic(path, lambda tmp: tmp.write_text(text, encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def utc_now() -> str:
    """The current time in UTC to the second, as written into metadata and reports."""
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
