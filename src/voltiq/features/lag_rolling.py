"""Lag and rolling window features for time-series forecasting."""
from __future__ import annotations

import numpy as np
import pandas as pd

from voltiq.config.settings import settings


def add_lag_features(
    df: pd.DataFrame,
    target_col: str = "sessions_per_hour",
    group_col: str = "station_id",
    lag_hours: list[int] | None = None,
) -> pd.DataFrame:
    """Add lag features over *lag_hours* for each station group.

    Operates on a *sorted* hourly-aggregated DataFrame.
    """
    df = df.copy()
    lag_hours = lag_hours or settings.lag_hours

    for lag in lag_hours:
        col_name = f"lag_{lag}h"
        df[col_name] = df.groupby(group_col)[target_col].shift(lag)

    return df


def add_rolling_features(
    df: pd.DataFrame,
    target_col: str = "sessions_per_hour",
    group_col: str = "station_id",
    windows: list[int] | None = None,
) -> pd.DataFrame:
    """Add rolling mean and std features within each station group."""
    df = df.copy()
    windows = windows or settings.rolling_windows

    for w in windows:
        # min_periods=1 so the first few rows are not all NaN
        rolled = df.groupby(group_col)[target_col].transform(
            lambda x, w=w: x.shift(1).rolling(w, min_periods=1).mean()
        )
        df[f"rolling_mean_{w}h"] = rolled

        rolled_std = df.groupby(group_col)[target_col].transform(
            lambda x, w=w: x.shift(1).rolling(w, min_periods=1).std().fillna(0)
        )
        df[f"rolling_std_{w}h"] = rolled_std

    return df


def build_hourly_aggregate(sessions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate session-level data into an hourly panel per station.

    Returns one row per (station_id, hour_bucket) with demand metrics.
    """
    df = sessions.copy()
    df["hour_bucket"] = df["start_time"].dt.floor("h")

    agg = (
        df.groupby(["station_id", "hour_bucket"])
        .agg(
            sessions_per_hour=("session_id", "count"),
            total_energy_kwh=("energy_kwh", "sum"),
            avg_duration_hours=("duration_hours", "mean"),
            station_type=("station_type", "first"),
            location_type=("location_type", "first"),
            power_kw=("power_kw", "first"),
            num_ports=("num_ports", "first"),
            latitude=("latitude", "first"),
            longitude=("longitude", "first"),
            region=("region", "first"),
        )
        .reset_index()
    )

    # Utilization as fraction of hourly port capacity (1 session per port per hour = 100%)
    agg["utilization_rate"] = np.clip(
        agg["sessions_per_hour"] / agg["num_ports"], 0.0, 1.0
    )

    return agg.sort_values(["station_id", "hour_bucket"]).reset_index(drop=True)
