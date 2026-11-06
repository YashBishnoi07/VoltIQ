"""FastAPI dependency injection with lazy singleton fallback."""
from __future__ import annotations

import asyncio
from fastapi import Request

from api.services.analytics_service import AnalyticsService
from api.services.prediction_service import PredictionService
from api.services.station_service import StationService

_station_service: StationService | None = None
_analytics_service: AnalyticsService | None = None
_prediction_service: PredictionService | None = None


def get_prediction_service(request: Request) -> PredictionService:
    global _prediction_service
    if hasattr(request.app.state, "prediction_service"):
        return request.app.state.prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
        asyncio.run(_prediction_service.initialize())
    return _prediction_service


def get_analytics_service(request: Request) -> AnalyticsService:
    global _analytics_service
    if hasattr(request.app.state, "analytics_service"):
        return request.app.state.analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
        asyncio.run(_analytics_service.initialize())
    return _analytics_service


def get_station_service(request: Request) -> StationService:
    global _station_service
    if hasattr(request.app.state, "station_service"):
        return request.app.state.station_service
    if _station_service is None:
        _station_service = StationService()
        asyncio.run(_station_service.initialize())
    return _station_service
