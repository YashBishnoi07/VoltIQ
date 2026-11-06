"""Classification models for station utilization (Low / Medium / High)."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.utils.class_weight import compute_class_weight

try:
    import xgboost as xgb

    _XGB_AVAILABLE = True
except ImportError:
    _XGB_AVAILABLE = False

from voltiq.config.settings import settings

CLASSIFICATION_FEATURE_COLS = [
    "mean_sessions",
    "std_sessions",
    "mean_energy",
    "station_type_enc",
    "location_type_enc",
    "power_tier",
    "num_ports",
    "power_kw",
    "mean_utilization",
]

CLASS_LABELS = ["Low", "Medium", "High"]


def build_logreg_pipeline(C: float = 1.0) -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            C=C,
            class_weight="balanced",
            max_iter=1000,
            random_state=settings.random_seed,
        )),
    ])


def build_rf_classifier(n_estimators: int = 200, **kwargs: Any) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=n_estimators,
        class_weight="balanced",
        random_state=settings.random_seed,
        n_jobs=-1,
        **kwargs,
    )


def build_xgb_classifier(**kwargs: Any) -> Any:
    if not _XGB_AVAILABLE:
        raise ImportError("xgboost is not installed.")
    defaults: dict[str, Any] = {
        "n_estimators": 200,
        "learning_rate": 0.05,
        "max_depth": 5,
        "use_label_encoder": False,
        "eval_metric": "mlogloss",
        "random_state": settings.random_seed,
        "n_jobs": -1,
        "verbosity": 0,
    }
    defaults.update(kwargs)
    return xgb.XGBClassifier(**defaults)


def prepare_classification_dataset(
    station_summary: pd.DataFrame,
) -> tuple[pd.DataFrame, np.ndarray, LabelEncoder, list[str]]:
    """Return X, y (integer-encoded), LabelEncoder, and feature list."""
    available_cols = [c for c in CLASSIFICATION_FEATURE_COLS if c in station_summary.columns]
    df_clean = station_summary.dropna(subset=available_cols + ["utilization_class"])

    le = LabelEncoder()
    le.classes_ = np.array(CLASS_LABELS)
    # Map string labels to ints explicitly
    label_map = {label: i for i, label in enumerate(CLASS_LABELS)}
    y = df_clean["utilization_class"].map(label_map).values.astype(int)

    X = df_clean[available_cols]
    return X, y, le, available_cols
