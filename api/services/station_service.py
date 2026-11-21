"""Station service — loads station catalogue and summary from processed data."""
from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from voltiq.config.settings import settings
from voltiq.utils.logging import get_logger

logger = get_logger("station_service")


class StationService:
    def __init__(self) -> None:
        self._summary: pd.DataFrame | None = None

    async def initialize(self) -> None:
        summary_path = settings.data_processed_dir / "station_summary.csv"
        if not summary_path.exists():
            try:
                from scripts.train import main as run_train
                run_train()
            except Exception as e:
                logger.error("Auto-train failed", error=str(e))

        if summary_path.exists():
            self._summary = pd.read_csv(str(summary_path))
            logger.info("Station summary loaded", stations=len(self._summary))
        else:
            logger.warning("Station summary not found")
            self._summary = pd.DataFrame()

    def list_stations(
        self,
        station_type: Optional[str] = None,
        region: Optional[str] = None,
        utilization_class: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        if self._summary is None or self._summary.empty:
            return []
        df = self._summary.copy()
        if station_type:
            df = df[df["station_type"] == station_type]
        if region:
            df = df[df["region"] == region]
        if utilization_class:
            df = df[df["utilization_class"].astype(str) == utilization_class]
        return df.fillna(0).to_dict(orient="records")

    def get_station(self, station_id: str) -> dict[str, Any] | None:
        if self._summary is None or self._summary.empty:
            return None
        row = self._summary[self._summary["station_id"] == station_id]
        if row.empty:
            return None
        return row.iloc[0].fillna(0).to_dict()
