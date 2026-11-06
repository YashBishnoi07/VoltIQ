"""Fairness checks: compare model error rates across urban vs rural stations."""
from __future__ import annotations

import numpy as np
import pandas as pd

from voltiq.utils.logging import get_logger

logger = get_logger(__name__)


def fairness_check_regression(
    hourly_df: pd.DataFrame,
    y_pred: np.ndarray,
    y_true: np.ndarray,
    group_col: str = "location_type",
) -> dict[str, dict[str, float]]:
    """Compute MAE per location-type group to surface prediction bias.

    Lower-demand rural stations should not have proportionally higher errors,
    as that would bias capacity recommendations toward already-high-demand areas.
    """
    test_df = hourly_df.copy().iloc[: len(y_pred)]
    test_df["_pred"] = y_pred
    test_df["_true"] = y_true
    test_df["_abs_error"] = np.abs(y_pred - y_true)

    result: dict[str, dict[str, float]] = {}
    for group, sub in test_df.groupby(group_col):
        mae = float(sub["_abs_error"].mean())
        mean_demand = float(sub["_true"].mean())
        rel_mae = mae / mean_demand if mean_demand > 0 else 0.0
        result[str(group)] = {
            "mae": round(mae, 4),
            "mean_demand": round(mean_demand, 4),
            "relative_mae": round(rel_mae, 4),
            "n_samples": int(len(sub)),
        }
        logger.info("Fairness group", group=group, mae=mae, relative_mae=rel_mae)

    return result


def underserved_stations(station_summary: pd.DataFrame) -> pd.DataFrame:
    """Identify stations that are underserved relative to their region peers.

    A station is flagged underserved if it is in a low-utilization area but high local demand
    pressure (std > mean) — suggesting it needs capacity investment.
    """
    df = station_summary.copy()
    # Regional mean utilization benchmark
    region_mean = df.groupby("region")["mean_utilization"].transform("mean")
    df["region_mean_util"] = region_mean

    # Underserved: utilization > regional mean AND classified as Low
    df["is_underserved"] = (
        (df["utilization_class"] == "Low")
        & (df["mean_utilization"] > df["region_mean_util"] * 0.8)
        & (df["std_sessions"] > df["mean_sessions"] * 0.5)
    )
    return df[df["is_underserved"]].sort_values("mean_utilization", ascending=False)
