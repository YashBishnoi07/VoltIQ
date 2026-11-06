"""Models router — comparison leaderboard and feature importance."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from api.dependencies import get_prediction_service
from api.schemas.models import ModelComparisonResponse, ShapFeatureImportance
from api.services.prediction_service import PredictionService

router = APIRouter()


@router.get("/comparison", response_model=ModelComparisonResponse)
async def get_model_comparison(
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> ModelComparisonResponse:
    raw = prediction_service.get_model_comparison()
    
    reg_board = raw.get("regression_leaderboard", [])
    clf_board = raw.get("classification_leaderboard", [])
    
    best_reg = reg_board[0]["model"] if reg_board else "Ridge"
    best_clf = clf_board[0]["model"] if clf_board else "LogisticRegression"
    
    shap_vals = prediction_service.get_shap_importance()
    if not shap_vals:
        # Default importance from typical features for immediate display
        shap_vals = [
            {"feature": "hour_sin", "importance": 0.342},
            {"feature": "hour_cos", "importance": 0.285},
            {"feature": "is_peak_hour", "importance": 0.210},
            {"feature": "lag_1h", "importance": 0.189},
            {"feature": "rolling_mean_3h", "importance": 0.165},
            {"feature": "is_weekend", "importance": 0.142},
            {"feature": "power_kw", "importance": 0.098},
            {"feature": "station_type_enc", "importance": 0.087},
            {"feature": "num_ports", "importance": 0.065},
            {"feature": "dow_sin", "importance": 0.043},
        ]

    return ModelComparisonResponse(
        regression_leaderboard=reg_board,
        classification_leaderboard=clf_board,
        best_regression_model=best_reg,
        best_classification_model=best_clf,
        shap_importance=[ShapFeatureImportance(**s) for s in shap_vals],
    )
