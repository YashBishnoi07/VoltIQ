"""Stations router — listing, filtering, and detail lookups."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_station_service
from api.schemas.station import StationListResponse, StationOut
from api.services.station_service import StationService

router = APIRouter()


@router.get("", response_model=StationListResponse)
async def list_stations(
    station_type: Optional[str] = Query(None, description="L1, L2, or DC_Fast"),
    region: Optional[str] = Query(None, description="West, Mountain, Midwest, East"),
    utilization_class: Optional[str] = Query(None, description="Low, Medium, or High"),
    station_service: StationService = Depends(get_station_service),
) -> StationListResponse:
    stations = station_service.list_stations(
        station_type=station_type,
        region=region,
        utilization_class=utilization_class,
    )
    return StationListResponse(stations=stations, total=len(stations))


@router.get("/{station_id}", response_model=StationOut)
async def get_station(
    station_id: str,
    station_service: StationService = Depends(get_station_service),
) -> StationOut:
    station = station_service.get_station(station_id)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found")
    return StationOut(**station)
