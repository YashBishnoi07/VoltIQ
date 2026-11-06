import numpy as np
from voltiq.evaluation.metrics import regression_metrics, classification_metrics
from voltiq.models.regression import build_ridge_pipeline
from voltiq.models.classification import build_logreg_pipeline


def test_regression_metrics():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([1.1, 1.9, 3.2, 3.8])
    m = regression_metrics(y_true, y_pred)
    assert "mae" in m
    assert "rmse" in m
    assert "mape" in m
    assert "r2" in m
    assert m["mae"] > 0
    assert m["rmse"] > 0


def test_classification_metrics():
    y_true = np.array([0, 1, 2, 1, 0])
    y_pred = np.array([0, 1, 2, 0, 0])
    m = classification_metrics(y_true, y_pred, class_labels=["Low", "Medium", "High"])
    assert "accuracy" in m
    assert "f1_macro" in m
    assert m["accuracy"] == 0.8


def test_pipeline_instantiation():
    ridge = build_ridge_pipeline()
    assert hasattr(ridge, "fit")
    logreg = build_logreg_pipeline()
    assert hasattr(logreg, "fit")
