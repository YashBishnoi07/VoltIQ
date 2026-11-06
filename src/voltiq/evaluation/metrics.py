"""Regression and classification metrics, plus model comparison utilities."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Return MAE, RMSE, MAPE, and R² for regression predictions."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    # MAPE: mask zeros to avoid division errors
    mask = y_true != 0
    mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)
    r2 = float(r2_score(y_true, y_pred))
    return {"mae": round(mae, 4), "rmse": round(rmse, 4), "mape": round(mape, 4), "r2": round(r2, 4)}


def classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
    class_labels: list[str] | None = None,
) -> dict[str, Any]:
    """Return accuracy, precision, recall, F1, confusion matrix, and ROC-AUC."""
    labels = class_labels or [str(i) for i in sorted(set(y_true))]
    metrics: dict[str, Any] = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision_macro": round(float(precision_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "recall_macro": round(float(recall_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "f1_macro": round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "class_labels": labels,
    }
    if y_proba is not None and len(np.unique(y_true)) > 1:
        try:
            auc = roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro")
            metrics["roc_auc"] = round(float(auc), 4)
        except ValueError:
            metrics["roc_auc"] = None
    return metrics


def time_based_split(
    df: pd.DataFrame,
    date_col: str = "hour_bucket",
    test_days: int = 60,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a time-indexed DataFrame into train/test using the last *test_days* days as test."""
    cutoff = df[date_col].max() - pd.Timedelta(days=test_days)
    train = df[df[date_col] <= cutoff]
    test = df[df[date_col] > cutoff]
    return train, test
