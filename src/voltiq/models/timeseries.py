"""Time-series models: ARIMA (statsmodels) and Prophet."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

try:
    from statsmodels.tsa.arima.model import ARIMA

    _ARIMA_AVAILABLE = True
except ImportError:
    _ARIMA_AVAILABLE = False

try:
    from prophet import Prophet

    _PROPHET_AVAILABLE = True
except ImportError:
    _PROPHET_AVAILABLE = False


def fit_arima(
    series: pd.Series,
    order: tuple[int, int, int] = (2, 1, 2),
) -> Any:
    """Fit an ARIMA model to a univariate hourly demand series."""
    if not _ARIMA_AVAILABLE:
        raise ImportError("statsmodels is not installed.")
    model = ARIMA(series.values, order=order)
    return model.fit()


def predict_arima(fitted_model: Any, steps: int) -> np.ndarray:
    forecast = fitted_model.forecast(steps=steps)
    return np.maximum(forecast, 0)


def fit_prophet(
    hourly_df: pd.DataFrame,
    station_id: str,
    changepoint_prior_scale: float = 0.05,
) -> Any:
    """Fit a Prophet model for a single station's hourly demand."""
    if not _PROPHET_AVAILABLE:
        raise ImportError("prophet is not installed.")

    station_data = (
        hourly_df[hourly_df["station_id"] == station_id][["hour_bucket", "sessions_per_hour"]]
        .rename(columns={"hour_bucket": "ds", "sessions_per_hour": "y"})
        .dropna()
    )
    # Remove UTC timezone — Prophet requires naive datetimes
    if hasattr(station_data["ds"].dtype, "tz") and station_data["ds"].dt.tz is not None:
        station_data["ds"] = station_data["ds"].dt.tz_localize(None)

    model = Prophet(
        changepoint_prior_scale=changepoint_prior_scale,
        seasonality_mode="multiplicative",
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        uncertainty_samples=100,
    )
    model.fit(station_data)
    return model, station_data


def predict_prophet(
    model: Any,
    periods: int,
    freq: str = "h",
) -> pd.DataFrame:
    """Return Prophet forecast DataFrame with yhat, yhat_lower, yhat_upper."""
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    forecast["yhat"] = forecast["yhat"].clip(lower=0)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)
