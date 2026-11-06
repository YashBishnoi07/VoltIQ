"""Predictions router — demand forecasting, utilization classification, batch prediction, CSV upload."""
from __future__ import annotations

import io
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from api.dependencies import get_prediction_service
from api.schemas.predict import (
    BatchPredictRow,
    DemandForecastRequest,
    DemandForecastResponse,
    UtilizationRequest,
    UtilizationResponse,
)
from api.services.prediction_service import PredictionService

router = APIRouter()


@router.post("/demand", response_model=DemandForecastResponse)
async def predict_demand(
    payload: DemandForecastRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> DemandForecastResponse:
    forecast_points = prediction_service.forecast_demand(
        station_id=payload.station_id,
        horizon_hours=payload.horizon_hours,
        start_datetime=payload.start_datetime,
    )
    model_name = prediction_service._reg_meta.get("model_name", "Ridge")
    return DemandForecastResponse(
        station_id=payload.station_id,
        horizon_hours=payload.horizon_hours,
        forecast=forecast_points,
        model_used=model_name,
    )


@router.post("/utilization", response_model=UtilizationResponse)
async def predict_utilization(
    payload: UtilizationRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> UtilizationResponse:
    result = prediction_service.classify_utilization(payload.model_dump())
    return UtilizationResponse(**result)


@router.post("/batch-csv")
async def batch_predict_csv(
    file: UploadFile = File(...),
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> StreamingResponse:
    """Accepts a CSV file with station features, returns scored CSV."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

    results = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        pred_util = prediction_service.classify_utilization(row_dict)
        results.append({
            **row_dict,
            "predicted_utilization_class": pred_util["predicted_class"],
            "prediction_confidence": pred_util["confidence"],
            "prob_Low": pred_util["probabilities"].get("Low", 0.0),
            "prob_Medium": pred_util["probabilities"].get("Medium", 0.0),
            "prob_High": pred_util["probabilities"].get("High", 0.0),
        })

    out_df = pd.DataFrame(results)
    stream = io.StringIO()
    out_df.to_csv(stream, index=False)
    stream.seek(0)

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=voltiq_scored_predictions.csv"},
    )
