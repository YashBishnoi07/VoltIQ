"""Data ingestion: load from synthetic generator or ACN-Data."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from voltiq.config.settings import settings
from voltiq.data.generator import generate_sessions
from voltiq.utils.io import read_parquet, write_parquet
from voltiq.utils.logging import get_logger

logger = get_logger(__name__)


def load_raw_data(force_regenerate: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load raw sessions and stations DataFrames.

    Uses cached Parquet files if present unless *force_regenerate* is True.
    Switches between synthetic and real ACN data based on ``settings.data_source``.
    """
    raw_dir = settings.data_raw_dir
    raw_dir.mkdir(parents=True, exist_ok=True)
    sessions_path = raw_dir / "sessions.parquet"
    stations_path = raw_dir / "stations.parquet"

    if not force_regenerate and sessions_path.exists() and stations_path.exists():
        logger.info("Loading cached raw data", source=str(raw_dir))
        sessions = read_parquet(sessions_path)
        stations = read_parquet(stations_path)
        return sessions, stations

    if settings.data_source == "synthetic":
        logger.info(
            "Generating synthetic data",
            n_sessions=settings.synthetic_sessions,
            n_stations=settings.synthetic_stations,
        )
        sessions, stations = generate_sessions()
    else:
        sessions, stations = _load_acn_data()

    write_parquet(sessions, sessions_path)
    write_parquet(stations, stations_path)
    logger.info("Raw data saved", sessions=len(sessions), stations=len(stations))
    return sessions, stations


def _load_acn_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and normalize ACN-Data from local cache or API.

    Not implemented in the offline build — raises informatively.
    """
    raise NotImplementedError(
        "ACN-Data ingestion requires a valid ACN_API_KEY and internet access. "
        "Set DATA_SOURCE=synthetic for offline use."
    )
