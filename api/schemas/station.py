from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class StationOut(BaseModel):
    station_id: str
    station_type: str
    location_type: str
    connector_type: Optional[str] = "CCS"
    power_kw: float
    latitude: float
    longitude: float
    num_ports: int
    region: str
    mean_utilization: Optional[float] = None
    utilization_class: Optional[str] = None
    mean_sessions: Optional[float] = None
    total_sessions: Optional[float] = None
    mean_energy: Optional[float] = None


class StationListResponse(BaseModel):
    stations: list[StationOut]
    total: int
