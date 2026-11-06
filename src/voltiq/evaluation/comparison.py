"""Model comparison: runs all regressors and classifiers and returns a ranked leaderboard."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit, cross_validate

from voltiq.config.settings import settings
from voltiq.evaluation.metrics import classification_metrics, regression_metrics, time_based_split
from voltiq.models.classification import (
    build_logreg_pipeline,
    build_rf_classifier,
    build_xgb_classifier,
    prepare_classification_dataset,
)
from voltiq.models.regression import (
    build_lgb_regressor,
    build_rf_regressor,
    build_ridge_pipeline,
    build_xgb_regressor,
    prepare_regression_dataset,
)
from voltiq.utils.logging import get_logger

logger = get_logger(__name__)


def compare_regression_models(
    hourly_df: pd.DataFrame,
) -> tuple[list[dict[str, Any]], Any]:
    """Train all regression models on a time-based split and return leaderboard + best model."""
    X, y, feature_cols = prepare_regression_dataset(hourly_df)
    # Align with the hourly_df to get date info for split
    idx = hourly_df.dropna(subset=feature_cols + ["sessions_per_hour"]).index
    dates = hourly_df.loc[idx, "hour_bucket"]

    cutoff = dates.max() - pd.Timedelta(days=settings.test_size_days)
    train_mask = dates <= cutoff
    test_mask = dates > cutoff

    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]

    logger.info("Regression split", train=int(train_mask.sum()), test=int(test_mask.sum()))

    candidates: dict[str, Any] = {
        "Ridge": build_ridge_pipeline(),
        "RandomForest": build_rf_regressor(),
    }
    try:
        candidates["XGBoost"] = build_xgb_regressor()
    except ImportError:
        pass
    try:
        candidates["LightGBM"] = build_lgb_regressor()
    except ImportError:
        pass

    results: list[dict[str, Any]] = []
    best_model = None
    best_rmse = float("inf")
    best_model_name = ""

    for name, model in candidates.items():
        logger.info("Training", model=name)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        m = regression_metrics(y_test.values, y_pred)
        m["model"] = name
        m["feature_count"] = len(feature_cols)
        results.append(m)
        logger.info("Result", model=name, **{k: v for k, v in m.items() if k != "model"})
        if m["rmse"] < best_rmse:
            best_rmse = m["rmse"]
            best_model = model
            best_model_name = name

    results.sort(key=lambda r: r["rmse"])
    logger.info("Best regression model", model=best_model_name, rmse=best_rmse)
    return results, best_model, best_model_name, feature_cols, X_train, X_test, y_train, y_test


def compare_classification_models(
    station_summary: pd.DataFrame,
) -> tuple[list[dict[str, Any]], Any]:
    """Train all classifiers and return leaderboard + best model."""
    from voltiq.models.classification import CLASS_LABELS

    X, y, le, feature_cols = prepare_classification_dataset(station_summary)

    if len(X) < 10:
        logger.warning("Insufficient samples for classification", n=len(X))
        return [], None, "", le, feature_cols

    # Simple 80/20 split (station-level, not temporal)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    candidates: dict[str, Any] = {
        "LogisticRegression": build_logreg_pipeline(),
        "RandomForest": build_rf_classifier(),
    }
    try:
        candidates["XGBoost"] = build_xgb_classifier()
    except ImportError:
        pass

    results: list[dict[str, Any]] = []
    best_model = None
    best_f1 = -1.0
    best_model_name = ""

    for name, model in candidates.items():
        logger.info("Training classifier", model=name)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None
        m = classification_metrics(y_test, y_pred, y_proba, class_labels=CLASS_LABELS)
        m["model"] = name
        results.append(m)
        logger.info("Result", model=name, f1=m["f1_macro"])
        if m["f1_macro"] > best_f1:
            best_f1 = m["f1_macro"]
            best_model = model
            best_model_name = name

    results.sort(key=lambda r: r["f1_macro"], reverse=True)
    return results, best_model, best_model_name, le, feature_cols
