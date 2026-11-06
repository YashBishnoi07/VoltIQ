"""Insights router — underserved stations, equity analysis, and fairness."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter

from voltiq.config.settings import settings

router = APIRouter()


@router.get("/underserved")
async def get_underserved_stations() -> dict[str, Any]:
    file_path = settings.data_processed_dir / "underserved.csv"
    if not file_path.exists():
        return {"stations": [], "total": 0}
    
    df = pd.read_csv(str(file_path))
    return {
        "stations": df.fillna(0).to_dict(orient="records"),
        "total": len(df),
        "recommendation": (
            "These stations experience high peak demand variance despite modest mean utilization. "
            "Prioritize them for targeted capacity expansion to prevent localized congestion."
        ),
    }


@router.get("/fairness")
async def get_fairness_audit() -> dict[str, Any]:
    summary_path = settings.models_store_dir / "pipeline_summary.json"
    if summary_path.exists():
        data = json.loads(summary_path.read_text())
        fairness = data.get("fairness_by_location", {})
    else:
        fairness = {}

    return {
        "disparity_analysis": fairness,
        "ethical_framework": (
            "VoltIQ uses group-conditioned Mean Absolute Error across Urban, Suburban, and Rural "
            "clusters to ensure capacity recommendations do not reinforce pre-existing infrastructure disparities."
        ),
        "disclaimer": (
            "DECISION-SUPPORT NOTICE: Model outputs are statistical estimates with confidence intervals. "
            "They must not be used as sole justifications for capital allocation without field validation."
        ),
    }
