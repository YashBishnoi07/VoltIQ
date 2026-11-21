"""Analytics service — loads processed data and computes dashboard metrics."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from voltiq.config.settings import settings
from voltiq.utils.logging import get_logger

logger = get_logger("analytics_service")


class AnalyticsService:
    """Loads and caches the processed hourly panel for analytics queries."""

    def __init__(self) -> None:
        self._hourly: pd.DataFrame | None = None

    async def initialize(self) -> None:
        hourly_path = settings.data_processed_dir / "hourly_features.csv"
        if not hourly_path.exists():
            logger.info("Processed features not found — auto-generating dataset via train pipeline")
            try:
                from scripts.train import main as run_train
                run_train()
            except Exception as e:
                logger.error("Auto-train failed", error=str(e))

        if hourly_path.exists():
            self._hourly = pd.read_csv(str(hourly_path), parse_dates=["hour_bucket"])
            logger.info("Hourly data loaded", rows=len(self._hourly))
        else:
            logger.warning("Hourly features not found")
            self._hourly = pd.DataFrame()

    def get_overview(self) -> dict[str, Any]:
        if self._hourly is None or self._hourly.empty:
            return {}
        h = self._hourly
        return {
            "total_sessions": int(h["sessions_per_hour"].sum()),
            "total_kwh": round(float(h["total_energy_kwh"].sum()), 2),
            "avg_utilization": round(float(h["utilization_rate"].mean()), 4),
            "peak_hour": int(h.groupby("hour")["sessions_per_hour"].mean().idxmax()),
            "total_stations": int(h["station_id"].nunique()),
            "high_util_stations": int(
                (h.groupby("station_id")["utilization_rate"].mean() > settings.high_utilization_threshold).sum()
            ),
            "low_util_stations": int(
                (h.groupby("station_id")["utilization_rate"].mean() < settings.low_utilization_threshold).sum()
            ),
        }

    def get_hourly_demand(self) -> list[dict[str, Any]]:
        if self._hourly is None or self._hourly.empty:
            return []
        h = self._hourly
        hourly_agg = h.groupby("hour")["sessions_per_hour"].mean().reset_index()
        weekday = h[h["is_weekend"] == 0].groupby("hour")["sessions_per_hour"].mean()
        weekend = h[h["is_weekend"] == 1].groupby("hour")["sessions_per_hour"].mean()

        result = []
        for _, row in hourly_agg.iterrows():
            hr = int(row["hour"])
            result.append({
                "hour": hr,
                "avg_sessions": round(float(row["sessions_per_hour"]), 3),
                "weekday_avg": round(float(weekday.get(hr, 0)), 3),
                "weekend_avg": round(float(weekend.get(hr, 0)), 3),
            })
        return result

    def get_heatmap(self) -> list[dict[str, Any]]:
        if self._hourly is None or self._hourly.empty:
            return []
        h = self._hourly
        pivot = h.groupby(["day_of_week", "hour"])["sessions_per_hour"].mean()
        return [
            {"hour": int(hr), "day_of_week": int(dow), "avg_sessions": round(float(val), 3)}
            for (dow, hr), val in pivot.items()
        ]

    def get_statistical_tests(self) -> list[dict[str, Any]]:
        if self._hourly is None or self._hourly.empty:
            return []
        from voltiq.analysis.statistical_tests import (
            test_normality,
            test_peak_hours_anova,
            test_weekday_vs_weekend,
        )
        norm = test_normality(self._hourly["sessions_per_hour"], "sessions_per_hour")
        ww = test_weekday_vs_weekend(self._hourly)
        anova = test_peak_hours_anova(self._hourly)
        return [
            {
                "test_name": norm["test"],
                "statistic": norm["statistic"],
                "p_value": norm["p_value"],
                "significant": not norm["is_normal"],
                "interpretation": norm["interpretation"],
            },
            {
                "test_name": ww.test_name,
                "statistic": ww.statistic,
                "p_value": ww.p_value,
                "significant": ww.significant,
                "interpretation": ww.interpretation,
            },
            {
                "test_name": anova["test"],
                "statistic": anova["statistic"],
                "p_value": anova["p_value"],
                "significant": anova["significant"],
                "interpretation": anova["interpretation"],
            },
        ]
