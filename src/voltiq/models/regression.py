"""Regression models for demand forecasting."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    import xgboost as xgb

    _XGB_AVAILABLE = True
except ImportError:
    _XGB_AVAILABLE = False

try:
    import lightgbm as lgb

    _LGB_AVAILABLE = True
except ImportError:
    _LGB_AVAILABLE = False

from voltiq.config.settings import settings

REGRESSION_FEATURE_COLS = [
    "hour",
    "day_of_week",
    "month",
    "is_weekend",
    "is_peak_hour",
    "is_holiday",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "month_sin",
    "month_cos",
    "station_type_enc",
    "location_type_enc",
    "power_tier",
    "num_ports",
    "power_kw",
    "lag_1h",
    "lag_24h",
    "lag_168h",
    "rolling_mean_3h",
    "rolling_mean_6h",
    "rolling_mean_24h",
    "rolling_std_3h",
    "rolling_std_6h",
]


def build_ridge_pipeline(alpha: float = 1.0) -> Pipeline:
    """Linear regression with L2 regularisation."""
    return Pipeline([
        ("scaler", StandardScaler()),
        ("ridge", Ridge(alpha=alpha, random_state=settings.random_seed)),
    ])


def build_rf_regressor(
    n_estimators: int = 200,
    max_depth: int | None = 15,
    **kwargs: Any,
) -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=settings.random_seed,
        n_jobs=-1,
        **kwargs,
    )


def build_xgb_regressor(**kwargs: Any) -> Any:
    if not _XGB_AVAILABLE:
        raise ImportError("xgboost is not installed.")
    defaults: dict[str, Any] = {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": settings.random_seed,
        "n_jobs": -1,
        "verbosity": 0,
    }
    defaults.update(kwargs)
    return xgb.XGBRegressor(**defaults)


def build_lgb_regressor(**kwargs: Any) -> Any:
    if not _LGB_AVAILABLE:
        raise ImportError("lightgbm is not installed.")
    defaults: dict[str, Any] = {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": -1,
        "num_leaves": 63,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": settings.random_seed,
        "n_jobs": -1,
        "verbose": -1,
    }
    defaults.update(kwargs)
    return lgb.LGBMRegressor(**defaults)


def prepare_regression_dataset(
    hourly_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Extract feature matrix X, target y, and available feature column names."""
    available_cols = [c for c in REGRESSION_FEATURE_COLS if c in hourly_df.columns]
    df_clean = hourly_df.dropna(subset=available_cols + ["sessions_per_hour"])
    X = df_clean[available_cols]
    y = df_clean["sessions_per_hour"]
    return X, y, available_cols
