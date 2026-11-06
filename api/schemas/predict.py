from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DemandForecastRequest(BaseModel):
    station_id: str
    horizon_hours: int = Field(default=24, ge=1, le=168)
    start_datetime: Optional[datetime] = None


class ForecastPoint(BaseModel):
    datetime: str
    predicted_sessions: float
    lower_bound: float
    upper_bound: float
    is_peak: bool


class DemandForecastResponse(BaseModel):
    station_id: str
    horizon_hours: int
    forecast: list[ForecastPoint]
    model_used: str
    uncertainty_note: str = (
        "This is a decision-support tool. Predictions carry uncertainty — "
        "always validate against local context before making infrastructure decisions."
    )


class UtilizationRequest(BaseModel):
    station_type: str
    location_type: str
    power_kw: float = Field(ge=0)
    num_ports: int = Field(ge=1)
    mean_sessions: float = Field(ge=0)
    std_sessions: float = Field(ge=0)
    mean_energy: float = Field(ge=0)
    mean_utilization: float = Field(ge=0, le=1)


class UtilizationResponse(BaseModel):
    predicted_class: str
    probabilities: dict[str, float]
    confidence: float
    model_used: str
    ethics_notice: str = (
        "Classification is a decision-support signal. "
        "Results may not reflect temporary demand shifts or local events."
    )


class BatchPredictRow(BaseModel):
    station_id: str
    predicted_sessions: float
    predicted_class: str
    confidence: float
