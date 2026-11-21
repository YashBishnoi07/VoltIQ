from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Data source
    data_source: Literal["synthetic", "acn"] = "synthetic"

    # Synthetic generator
    synthetic_sessions: int = 50_000
    synthetic_stations: int = 30
    synthetic_start_date: str = "2023-01-01"
    synthetic_end_date: str = "2024-12-31"
    random_seed: int = 42

    # ACN
    acn_api_key: str = ""

    # Paths (relative to project root)
    data_raw_dir: Path = Path("data/raw")
    data_interim_dir: Path = Path("data/interim")
    data_processed_dir: Path = Path("data/processed")
    models_store_dir: Path = Path("models_store")

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    cors_origins: list[str] = Field(
        default=["*"]
    )

    # Logging
    log_level: str = "INFO"

    # Feature engineering constants
    peak_hours: list[int] = Field(default=[7, 8, 9, 17, 18, 19, 20])
    lag_hours: list[int] = Field(default=[1, 24, 168])
    rolling_windows: list[int] = Field(default=[3, 6, 12, 24])

    # Utilization thresholds (fraction of capacity)
    low_utilization_threshold: float = 0.35
    high_utilization_threshold: float = 0.70

    # Model training
    test_size_days: int = 60
    cv_splits: int = 5


settings = Settings()
