"""Find, archive and clean the EEG-Bewegungsdaten of the four German TSOs."""

from eeg_bewegungsdaten._version import __version__
from eeg_bewegungsdaten.ingest import scan
from eeg_bewegungsdaten.special_rows import generation, grid_feed_in

__all__ = ["__version__", "generation", "grid_feed_in", "scan"]
