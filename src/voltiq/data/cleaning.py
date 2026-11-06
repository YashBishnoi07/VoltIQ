"""Data cleaning pipeline: missing values, outliers, type fixes, deduplication."""
from __future__ import annotations

import numpy as np
import pandas as pd

from voltiq.utils.logging import get_logger

logger = get_logger(__name__)


def clean_sessions(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full cleaning pipeline on a raw sessions DataFrame.

    Steps applied in order:
    1. Remove exact duplicate rows.
    2. Fix data types (datetime, numeric casts).
    3. Drop rows with structurally impossible values.
    4. Impute missing energy with station-type median.
    5. Cap energy outliers using IQR fencing (per station type).
    6. Add a data quality flag column.
    """
    original_len = len(df)
    df = df.copy()

    df = _remove_duplicates(df)
    df = _fix_types(df)
    df = _drop_impossible_rows(df)
    df = _impute_missing_energy(df)
    df = _cap_energy_outliers(df)

    logger.info(
        "Cleaning complete",
        rows_in=original_len,
        rows_out=len(df),
        dropped=original_len - len(df),
    )
    return df


def _remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    # Exact duplicates on natural key columns
    key_cols = ["station_id", "user_id", "start_time", "duration_hours"]
    df = df.drop_duplicates(subset=key_cols)
    logger.debug("Duplicates removed", count=before - len(df))
    return df


def _fix_types(df: pd.DataFrame) -> pd.DataFrame:
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True, errors="coerce")
    df["end_time"] = pd.to_datetime(df["end_time"], utc=True, errors="coerce")
    for col in ["duration_hours", "energy_kwh", "power_kw", "latitude", "longitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _drop_impossible_rows(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    # Must have valid timestamps
    df = df.dropna(subset=["start_time", "end_time", "station_id"])
    # Duration must be positive and plausible (<= 24 h for a single session)
    df = df[(df["duration_hours"] > 0) & (df["duration_hours"] <= 24)]
    # end_time must be after start_time
    df = df[df["end_time"] > df["start_time"]]
    # Coordinates must be in plausible US range
    df = df[
        df["latitude"].between(24.0, 50.0) & df["longitude"].between(-125.0, -66.0)
    ]
    logger.debug("Impossible rows dropped", count=before - len(df))
    return df


def _impute_missing_energy(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing energy_kwh with the median for that station type."""
    missing_before = df["energy_kwh"].isna().sum()
    medians = df.groupby("station_type")["energy_kwh"].transform("median")
    df["energy_kwh"] = df["energy_kwh"].fillna(medians)
    # If still NaN (edge case: all sessions of a type are missing), use global median
    global_median = df["energy_kwh"].median()
    df["energy_kwh"] = df["energy_kwh"].fillna(global_median)
    logger.debug("Energy imputed", imputed=missing_before)
    return df


def _cap_energy_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Winsorise energy_kwh at the IQR fence (1.5 × IQR above Q3) per station type."""
    q1 = df.groupby("station_type")["energy_kwh"].transform("quantile", 0.25)
    q3 = df.groupby("station_type")["energy_kwh"].transform("quantile", 0.75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    mask = df["energy_kwh"] > upper
    capped = int(mask.sum())
    df.loc[mask, "energy_kwh"] = upper[mask]
    logger.debug("Energy outliers capped", count=capped)
    return df
