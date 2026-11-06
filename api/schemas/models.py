from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class RegressionResult(BaseModel):
    model: str
    mae: float
    rmse: float
    mape: float
    r2: float
    feature_count: Optional[int] = None


class ClassificationResult(BaseModel):
    model: str
    accuracy: float
    f1_macro: float
    roc_auc: Optional[float] = None
    confusion_matrix: list[list[int]]
    class_labels: list[str]


class ShapFeatureImportance(BaseModel):
    feature: str
    importance: float


class ModelComparisonResponse(BaseModel):
    regression_leaderboard: list[RegressionResult]
    classification_leaderboard: list[ClassificationResult]
    best_regression_model: str
    best_classification_model: str
    shap_importance: list[ShapFeatureImportance]
