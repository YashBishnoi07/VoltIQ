from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class OverviewResponse(BaseModel):
    total_sessions: int
    total_kwh: float
    avg_utilization: float
    peak_hour: int
    total_stations: int
    high_util_stations: int
    low_util_stations: int


class HourlyDemandPoint(BaseModel):
    hour: int
    avg_sessions: float
    weekday_avg: float
    weekend_avg: float


class HeatmapCell(BaseModel):
    hour: int
    day_of_week: int
    avg_sessions: float


class AnalyticsHourlyResponse(BaseModel):
    data: list[HourlyDemandPoint]


class AnalyticsHeatmapResponse(BaseModel):
    data: list[HeatmapCell]


class StatTestResult(BaseModel):
    test_name: str
    statistic: float
    p_value: float
    significant: bool
    interpretation: str
