"""Analytics router — overview KPI, hourly patterns, heatmap, and statistical test results."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from api.dependencies import get_analytics_service
from api.schemas.analytics import (
    AnalyticsHeatmapResponse,
    AnalyticsHourlyResponse,
    OverviewResponse,
    StatTestResult,
)
from api.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/overview", response_model=OverviewResponse)
async def get_overview(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> OverviewResponse:
    data = analytics_service.get_overview()
    return OverviewResponse(**data)


@router.get("/hourly", response_model=AnalyticsHourlyResponse)
async def get_hourly_demand(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsHourlyResponse:
    data = analytics_service.get_hourly_demand()
    return AnalyticsHourlyResponse(data=data)


@router.get("/heatmap", response_model=AnalyticsHeatmapResponse)
async def get_heatmap(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsHeatmapResponse:
    data = analytics_service.get_heatmap()
    return AnalyticsHeatmapResponse(data=data)


@router.get("/stats", response_model=list[StatTestResult])
async def get_statistical_tests(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> list[StatTestResult]:
    tests = analytics_service.get_statistical_tests()
    return [StatTestResult(**t) for t in tests]
