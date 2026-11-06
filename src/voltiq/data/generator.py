"""Realistic synthetic EV charging session generator.

Design decisions:
- Morning (7-9 AM) and evening (5-8 PM) peaks modelled with Gaussian bumps on top of a
  low base rate so the distribution matches empirical ACN-Data patterns.
- Weekend sessions skew toward midday and have ~20% lower total volume.
- Fast chargers (DC) produce shorter, higher-energy sessions; overnight chargers (L2)
  produce long, low-power sessions — matching real behavioural clusters.
- Noise is added via multiplicative log-normal jitter so variance scales with mean.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from voltiq.config.settings import settings
from voltiq.utils.seed import set_global_seed

# ---------------------------------------------------------------------------
# Station metadata catalogue
# ---------------------------------------------------------------------------

STATION_TYPES = ["L1", "L2", "DC_Fast"]
LOCATION_TYPES = ["urban", "suburban", "highway", "rural"]
CONNECTOR_TYPES = ["J1772", "CCS", "CHAdeMO", "Tesla"]

# kW capacity per station type
CHARGER_POWER_KW: dict[str, tuple[float, float]] = {
    "L1": (1.4, 1.9),
    "L2": (6.2, 11.5),
    "DC_Fast": (50.0, 150.0),
}

# Typical session duration hours: (mean, std)
SESSION_DURATION_HOURS: dict[str, tuple[float, float]] = {
    "L1": (8.0, 2.5),
    "L2": (3.5, 1.8),
    "DC_Fast": (0.6, 0.25),
}


@dataclass
class StationSpec:
    station_id: str
    station_type: str
    location_type: str
    connector_type: str
    power_kw: float
    latitude: float
    longitude: float
    num_ports: int
    region: str


def _build_station_catalogue(n: int, rng: np.random.Generator) -> list[StationSpec]:
    """Generate a fixed station catalogue with realistic geographic spread."""
    # US bounding box roughly covering major metro + highway corridors
    lat_bounds = (33.0, 47.5)
    lon_bounds = (-122.5, -73.5)

    location_weights = [0.45, 0.30, 0.15, 0.10]
    type_weights = [0.10, 0.60, 0.30]

    stations: list[StationSpec] = []
    for i in range(n):
        s_type = rng.choice(STATION_TYPES, p=type_weights)
        loc_type = rng.choice(LOCATION_TYPES, p=location_weights)

        pwr_min, pwr_max = CHARGER_POWER_KW[s_type]
        power_kw = float(rng.uniform(pwr_min, pwr_max))

        connector = rng.choice(
            CONNECTOR_TYPES,
            p=[0.40, 0.30, 0.15, 0.15] if s_type != "DC_Fast" else [0.05, 0.50, 0.30, 0.15],
        )

        lat = float(rng.uniform(*lat_bounds))
        lon = float(rng.uniform(*lon_bounds))

        # Urban clusters near major metros; highway stations on east-west corridors
        if loc_type == "urban":
            lat = float(np.clip(lat + rng.normal(0, 2), *lat_bounds))
            lon = float(np.clip(lon + rng.normal(0, 2), *lon_bounds))

        num_ports = int(rng.choice([2, 4, 6, 8, 12], p=[0.20, 0.35, 0.25, 0.15, 0.05]))

        region = _assign_region(lat, lon)

        stations.append(
            StationSpec(
                station_id=f"STN-{i+1:04d}",
                station_type=s_type,
                location_type=loc_type,
                connector_type=connector,
                power_kw=round(power_kw, 2),
                latitude=round(lat, 6),
                longitude=round(lon, 6),
                num_ports=num_ports,
                region=region,
            )
        )
    return stations


def _assign_region(lat: float, lon: float) -> str:
    if lon < -105:
        return "West"
    if lon < -90:
        return "Mountain"
    if lon < -78:
        return "Midwest"
    return "East"


# ---------------------------------------------------------------------------
# Demand profile helpers
# ---------------------------------------------------------------------------

def _hourly_demand_weight(hour: int, is_weekend: bool) -> float:
    """Return a relative demand weight for a given hour.

    Uses two Gaussian bumps (morning and evening peaks) on a low overnight base.
    Weekend profile is flatter and shifted toward midday.
    """
    if is_weekend:
        # Single midday bump
        return 0.3 + 1.0 * np.exp(-0.5 * ((hour - 13) / 3.5) ** 2)
    # Weekday double-peak
    morning = 1.2 * np.exp(-0.5 * ((hour - 8) / 1.5) ** 2)
    evening = 1.5 * np.exp(-0.5 * ((hour - 18) / 2.0) ** 2)
    base = 0.15
    return base + morning + evening


def _seasonal_multiplier(month: int) -> float:
    """Higher EV charging in summer (road trips) and dip in deep winter."""
    # Peaks in July (7) with a secondary peak in December (holiday travel)
    summer = 0.25 * np.exp(-0.5 * ((month - 7) / 2.5) ** 2)
    winter_dip = -0.10 * np.exp(-0.5 * ((month - 1) / 1.5) ** 2)
    return 1.0 + summer + winter_dip


# ---------------------------------------------------------------------------
# Session generator
# ---------------------------------------------------------------------------

def generate_sessions(
    n_sessions: int | None = None,
    n_stations: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    seed: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate synthetic EV charging sessions.

    Returns
    -------
    sessions : pd.DataFrame
        One row per charging session.
    stations : pd.DataFrame
        Station metadata catalogue.
    """
    n_sessions = n_sessions or settings.synthetic_sessions
    n_stations = n_stations or settings.synthetic_stations
    start_date = start_date or settings.synthetic_start_date
    end_date = end_date or settings.synthetic_end_date
    seed = seed if seed is not None else settings.random_seed

    set_global_seed(seed)
    rng = np.random.default_rng(seed)

    station_list = _build_station_catalogue(n_stations, rng)
    stations_df = pd.DataFrame([s.__dict__ for s in station_list])

    date_range = pd.date_range(start=start_date, end=end_date, freq="h")
    n_hours = len(date_range)

    # Pre-compute weights for each hour slot
    weights = np.array(
        [
            _hourly_demand_weight(ts.hour, ts.dayofweek >= 5) * _seasonal_multiplier(ts.month)
            for ts in date_range
        ]
    )
    weights = np.maximum(weights, 0.01)
    weights /= weights.sum()

    # Sample which hour each session falls into
    session_hour_indices = rng.choice(n_hours, size=n_sessions, p=weights)
    session_timestamps = date_range[session_hour_indices]

    # Add sub-hour jitter
    jitter_minutes = rng.integers(0, 60, size=n_sessions)
    session_starts = session_timestamps + pd.to_timedelta(jitter_minutes, unit="m")

    # Assign sessions to stations (weighted toward busier station types)
    station_weights = np.array(
        [2.0 if s.location_type == "urban" else 1.0 for s in station_list]
    )
    station_weights /= station_weights.sum()
    station_indices = rng.choice(n_stations, size=n_sessions, p=station_weights)
    assigned_stations = [station_list[i] for i in station_indices]

    # Compute session duration and energy
    durations: list[float] = []
    energies: list[float] = []
    for st in assigned_stations:
        mu, sigma = SESSION_DURATION_HOURS[st.station_type]
        dur = float(np.clip(rng.normal(mu, sigma), 0.1, mu * 3))
        # Log-normal noise on power delivery (connector efficiency, state-of-charge)
        power_jitter = float(np.exp(rng.normal(0, 0.15)))
        energy = dur * st.power_kw * power_jitter
        durations.append(round(dur, 3))
        energies.append(round(energy, 3))

    # Anonymise user IDs (hash so we can track sessions without PII)
    raw_user_ids = rng.integers(1, n_sessions // 3, size=n_sessions)
    user_ids = [
        hashlib.sha256(f"user_{uid}_{seed}".encode()).hexdigest()[:12]
        for uid in raw_user_ids
    ]

    sessions = pd.DataFrame(
        {
            "session_id": [f"SES-{i+1:07d}" for i in range(n_sessions)],
            "station_id": [s.station_id for s in assigned_stations],
            "user_id": user_ids,
            "start_time": session_starts,
            "duration_hours": durations,
            "energy_kwh": energies,
            "station_type": [s.station_type for s in assigned_stations],
            "location_type": [s.location_type for s in assigned_stations],
            "connector_type": [s.connector_type for s in assigned_stations],
            "power_kw": [s.power_kw for s in assigned_stations],
            "latitude": [s.latitude for s in assigned_stations],
            "longitude": [s.longitude for s in assigned_stations],
            "region": [s.region for s in assigned_stations],
            "num_ports": [s.num_ports for s in assigned_stations],
        }
    )

    sessions["end_time"] = sessions["start_time"] + pd.to_timedelta(
        sessions["duration_hours"], unit="h"
    )
    sessions = sessions.sort_values("start_time").reset_index(drop=True)

    # Inject a small fraction of realistic anomalies (duplicates, missing values, outliers)
    sessions = _inject_anomalies(sessions, rng)

    return sessions, stations_df


def _inject_anomalies(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Inject realistic data quality issues for the cleaning module to handle."""
    n = len(df)

    # ~0.5% duplicate rows
    dup_idx = rng.choice(n, size=int(n * 0.005), replace=False)
    duplicates = df.iloc[dup_idx].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    # ~1% missing energy values
    missing_idx = rng.choice(len(df), size=int(len(df) * 0.01), replace=False)
    df.loc[missing_idx, "energy_kwh"] = np.nan

    # ~0.3% extreme outlier sessions (data entry errors — 10× normal energy)
    outlier_idx = rng.choice(len(df), size=int(len(df) * 0.003), replace=False)
    df.loc[outlier_idx, "energy_kwh"] = df.loc[outlier_idx, "energy_kwh"] * 10

    return df
