"""Hyperparameter tuning with Optuna."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

try:
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    _OPTUNA_AVAILABLE = True
except ImportError:
    _OPTUNA_AVAILABLE = False

from voltiq.config.settings import settings
from voltiq.evaluation.metrics import regression_metrics
from voltiq.models.regression import build_xgb_regressor
from voltiq.utils.logging import get_logger

logger = get_logger(__name__)


def tune_xgb_regressor(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_trials: int = 30,
) -> dict[str, Any]:
    """Tune XGBoost regressor with Optuna and return best params."""
    if not _OPTUNA_AVAILABLE:
        logger.warning("Optuna not available, skipping tuning")
        return {}

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 1.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 1.0, log=True),
        }
        model = build_xgb_regressor(**params)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)
        return regression_metrics(y_val.values, y_pred)["rmse"]

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=settings.random_seed),
    )
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    logger.info("Tuning complete", best_rmse=study.best_value, params=study.best_params)
    return study.best_params
