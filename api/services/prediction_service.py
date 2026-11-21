"""Prediction service — loads trained models and runs inference."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from voltiq.config.settings import settings
from voltiq.utils.logging import get_logger

logger = get_logger("prediction_service")

_PARQUET_ENGINE = "fastparquet"


class PredictionService:
    def __init__(self) -> None:
        self._reg_model: Any = None
        self._reg_meta: dict[str, Any] = {}
        self._clf_model: Any = None
        self._clf_meta: dict[str, Any] = {}
        self._hourly: pd.DataFrame | None = None
        self._model_comparison: dict[str, Any] = {}

    async def initialize(self) -> None:
        from voltiq.models.registry import load_latest_model, list_saved_models

        try:
            self._reg_model, self._reg_meta = load_latest_model("regression")
        except FileNotFoundError:
            logger.warning("No regression model found — predictions will return zeros")

        try:
            self._clf_model, self._clf_meta = load_latest_model("classification")
        except FileNotFoundError:
            logger.warning("No classification model found")

        hourly_path = settings.data_processed_dir / "hourly_features.csv"
        if hourly_path.exists():
            self._hourly = pd.read_csv(str(hourly_path), parse_dates=["hour_bucket"])

        summary_path = settings.models_store_dir / "pipeline_summary.json"
        if summary_path.exists():
            self._model_comparison = json.loads(summary_path.read_text())

        logger.info("PredictionService ready",
                    reg_model=self._reg_meta.get("model_name", "none"),
                    clf_model=self._clf_meta.get("model_name", "none"))

    def forecast_demand(
        self,
        station_id: str,
        horizon_hours: int = 24,
        start_datetime: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Generate demand forecast for a station over a horizon."""
        if self._reg_model is None:
            return self._fallback_forecast(station_id, horizon_hours, start_datetime)

        feature_cols = self._reg_meta.get("feature_cols", [])
        start = start_datetime or datetime.now(timezone.utc)

        forecast_rows = []
        for h in range(horizon_hours):
            ts = pd.Timestamp(start) + pd.Timedelta(hours=h)
            row = self._build_forecast_row(station_id, ts, feature_cols)
            if row is None:
                pred = 0.0
            else:
                pred = float(self._reg_model.predict(row)[0])
                pred = max(pred, 0)

            # Uncertainty: simple ±15% interval (replace with SHAP-based CI in future)
            margin = pred * 0.15
            is_peak = ts.hour in settings.peak_hours

            forecast_rows.append({
                "datetime": ts.isoformat(),
                "predicted_sessions": round(pred, 3),
                "lower_bound": round(max(pred - margin, 0), 3),
                "upper_bound": round(pred + margin, 3),
                "is_peak": is_peak,
            })
        return forecast_rows

    def _build_forecast_row(
        self,
        station_id: str,
        ts: pd.Timestamp,
        feature_cols: list[str],
    ) -> pd.DataFrame | None:
        """Build a single-row feature DataFrame for a future timestamp."""
        import holidays as holidays_lib

        us_holidays = holidays_lib.US(years=[ts.year])
        is_weekend = 1 if ts.dayofweek >= 5 else 0
        is_peak = 1 if ts.hour in settings.peak_hours else 0
        is_holiday = 1 if ts.date() in us_holidays else 0

        # Get station-level features from last known record
        station_row: dict[str, Any] = {}
        if self._hourly is not None and not self._hourly.empty:
            station_hist = self._hourly[self._hourly["station_id"] == station_id]
            if not station_hist.empty:
                last = station_hist.iloc[-1]
                station_row = last.to_dict()

        row: dict[str, Any] = {
            "hour": ts.hour,
            "day_of_week": ts.dayofweek,
            "month": ts.month,
            "is_weekend": is_weekend,
            "is_peak_hour": is_peak,
            "is_holiday": is_holiday,
            "hour_sin": float(np.sin(2 * np.pi * ts.hour / 24)),
            "hour_cos": float(np.cos(2 * np.pi * ts.hour / 24)),
            "dow_sin": float(np.sin(2 * np.pi * ts.dayofweek / 7)),
            "dow_cos": float(np.cos(2 * np.pi * ts.dayofweek / 7)),
            "month_sin": float(np.sin(2 * np.pi * (ts.month - 1) / 12)),
            "month_cos": float(np.cos(2 * np.pi * (ts.month - 1) / 12)),
        }
        # Merge station-level features
        for col in feature_cols:
            if col not in row and col in station_row:
                row[col] = station_row[col]
            elif col not in row:
                row[col] = 0

        available = {c: row[c] for c in feature_cols if c in row}
        if len(available) < len(feature_cols):
            missing = [c for c in feature_cols if c not in available]
            for m in missing:
                available[m] = 0

        return pd.DataFrame([available])[feature_cols]

    def _fallback_forecast(
        self,
        station_id: str,
        horizon_hours: int,
        start_datetime: Optional[datetime],
    ) -> list[dict[str, Any]]:
        start = start_datetime or datetime.now(timezone.utc)
        result = []
        for h in range(horizon_hours):
            ts = pd.Timestamp(start) + pd.Timedelta(hours=h)
            result.append({
                "datetime": ts.isoformat(),
                "predicted_sessions": 0.0,
                "lower_bound": 0.0,
                "upper_bound": 0.0,
                "is_peak": ts.hour in settings.peak_hours,
            })
        return result

    def classify_utilization(self, features: dict[str, Any]) -> dict[str, Any]:
        """Classify a station's utilization from its feature profile."""
        from voltiq.models.classification import CLASS_LABELS, CLASSIFICATION_FEATURE_COLS

        if self._clf_model is None:
            return {
                "predicted_class": "Medium",
                "probabilities": {"Low": 0.33, "Medium": 0.34, "High": 0.33},
                "confidence": 0.34,
                "model_used": "none",
            }

        feature_cols = self._clf_meta.get("feature_cols", CLASSIFICATION_FEATURE_COLS)

        # Encode categorical inputs
        type_order = {"L1": 0, "L2": 1, "DC_Fast": 2}
        loc_order = {"rural": 0, "suburban": 1, "highway": 2, "urban": 3}
        power_kw = float(features.get("power_kw", 7.0))

        row = {
            "station_type_enc": type_order.get(features.get("station_type", "L2"), 1),
            "location_type_enc": loc_order.get(features.get("location_type", "urban"), 3),
            "power_tier": 0 if power_kw <= 3 else 1 if power_kw <= 15 else 2 if power_kw <= 50 else 3,
            "num_ports": int(features.get("num_ports", 4)),
            "power_kw": power_kw,
            "mean_sessions": float(features.get("mean_sessions", 2.0)),
            "std_sessions": float(features.get("std_sessions", 1.0)),
            "mean_energy": float(features.get("mean_energy", 10.0)),
            "mean_utilization": float(features.get("mean_utilization", 0.4)),
        }

        X = pd.DataFrame([{c: row.get(c, 0) for c in feature_cols}])
        pred = int(self._clf_model.predict(X)[0])
        proba = self._clf_model.predict_proba(X)[0]

        label = CLASS_LABELS[pred]
        proba_dict = {cls: round(float(p), 4) for cls, p in zip(CLASS_LABELS, proba)}

        return {
            "predicted_class": label,
            "probabilities": proba_dict,
            "confidence": round(float(proba[pred]), 4),
            "model_used": self._clf_meta.get("model_name", "unknown"),
        }

    def get_model_comparison(self) -> dict[str, Any]:
        return self._model_comparison

    def get_shap_importance(self) -> list[dict[str, Any]]:
        """Compute SHAP feature importances from the best regression model."""
        if self._reg_model is None or self._hourly is None or self._hourly.empty:
            return []
        try:
            import shap

            feature_cols = self._reg_meta.get("feature_cols", [])
            if not feature_cols:
                return []
            df = self._hourly.dropna(subset=feature_cols)
            X_sample = df[feature_cols].head(500)

            explainer = shap.Explainer(self._reg_model, X_sample)
            shap_values = explainer(X_sample)
            importance = np.abs(shap_values.values).mean(axis=0)
            ranked = sorted(
                zip(feature_cols, importance), key=lambda x: x[1], reverse=True
            )
            return [{"feature": f, "importance": round(float(v), 6)} for f, v in ranked[:15]]
        except Exception as e:
            logger.warning("SHAP computation failed", error=str(e))
            return []
