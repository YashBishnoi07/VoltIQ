"""Temporal feature engineering: calendar, peak flags, holidays."""
from __future__ import annotations

import pandas as pd

try:
    import holidays as holidays_lib

    _HOLIDAYS_AVAILABLE = True
except ImportError:
    _HOLIDAYS_AVAILABLE = False

from voltiq.config.settings import settings


def add_temporal_features(df: pd.DataFrame, timestamp_col: str = "start_time") -> pd.DataFrame:
    """Add calendar and peak-hour features derived from *timestamp_col*."""
    df = df.copy()
    ts = df[timestamp_col]

    df["hour"] = ts.dt.hour
    df["day_of_week"] = ts.dt.dayofweek  # 0=Monday
    df["day_of_month"] = ts.dt.day
    df["month"] = ts.dt.month
    df["quarter"] = ts.dt.quarter
    df["year"] = ts.dt.year
    df["week_of_year"] = ts.dt.isocalendar().week.astype("int32")
    df["is_weekend"] = (df["day_of_week"] >= 5).astype("int8")
    df["is_peak_hour"] = df["hour"].isin(settings.peak_hours).astype("int8")

    # Cyclical encoding so models see hour 23 ≈ hour 0
    df["hour_sin"] = _sin_encode(df["hour"], 24)
    df["hour_cos"] = _cos_encode(df["hour"], 24)
    df["dow_sin"] = _sin_encode(df["day_of_week"], 7)
    df["dow_cos"] = _cos_encode(df["day_of_week"], 7)
    df["month_sin"] = _sin_encode(df["month"] - 1, 12)
    df["month_cos"] = _cos_encode(df["month"] - 1, 12)

    if _HOLIDAYS_AVAILABLE:
        df = _add_holiday_flag(df, timestamp_col)
    else:
        df["is_holiday"] = 0

    return df


def _sin_encode(series: pd.Series, period: int) -> pd.Series:
    import numpy as np

    return np.sin(2 * np.pi * series / period)


def _cos_encode(series: pd.Series, period: int) -> pd.Series:
    import numpy as np

    return np.cos(2 * np.pi * series / period)


def _add_holiday_flag(df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
    us_holidays = holidays_lib.US(years=df[timestamp_col].dt.year.unique().tolist())
    dates = df[timestamp_col].dt.date
    df["is_holiday"] = dates.apply(lambda d: 1 if d in us_holidays else 0).astype("int8")
    return df
