"""Shared HTTP client settings."""

from __future__ import annotations

import httpx

from eeg_bewegungsdaten._version import __version__

USER_AGENT = f"eeg-bewegungsdaten/{__version__}"


def new_client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
        timeout=httpx.Timeout(30.0, read=120.0),
        transport=httpx.HTTPTransport(retries=2),
    )
