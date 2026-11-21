"""FastAPI application entry point."""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from voltiq.config.settings import settings
from voltiq.utils.logging import configure_logging, get_logger

configure_logging(settings.log_level)
logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("VoltIQ API starting up")
    from api.services.prediction_service import PredictionService
    from api.services.analytics_service import AnalyticsService
    from api.services.station_service import StationService

    app.state.prediction_service = PredictionService()
    app.state.analytics_service = AnalyticsService()
    app.state.station_service = StationService()

    await app.state.prediction_service.initialize()
    await app.state.analytics_service.initialize()
    await app.state.station_service.initialize()

    logger.info("Services initialized")
    yield
    logger.info("VoltIQ API shutting down")


app = FastAPI(
    title="VoltIQ API",
    description="EV Charging Demand Forecasting & Station Utilization Intelligence",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):  # type: ignore[no-untyped-def]
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "Request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration_ms, 2),
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled error", path=request.url.path, error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Register routers
from api.routers import analytics, health, insights, models, predict, stations  # noqa: E402

app.include_router(health.router)
app.include_router(stations.router, prefix="/stations", tags=["Stations"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(predict.router, prefix="/predict", tags=["Predictions"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])
