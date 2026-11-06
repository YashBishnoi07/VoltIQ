"""Station-level feature engineering: type encoding, connector encoding, derived metrics."""
from __future__ import annotations

import pandas as pd
from sklearn.preprocessing import LabelEncoder


def add_station_features(df: pd.DataFrame) -> pd.DataFrame:
    """Encode categorical station attributes and add derived station-level metrics."""
    df = df.copy()

    # Ordinal encoding for station type (L1=0, L2=1, DC_Fast=2 — natural power order)
    type_order = {"L1": 0, "L2": 1, "DC_Fast": 2}
    df["station_type_enc"] = df["station_type"].map(type_order).fillna(1).astype("int8")

    loc_order = {"rural": 0, "suburban": 1, "highway": 2, "urban": 3}
    df["location_type_enc"] = df["location_type"].map(loc_order).fillna(1).astype("int8")

    # One-hot encode connector type (drop first to avoid multicollinearity)
    if "connector_type" in df.columns:
        connector_dummies = pd.get_dummies(
            df["connector_type"], prefix="conn", drop_first=True, dtype="int8"
        )
        df = pd.concat([df, connector_dummies], axis=1)

    # Power tier bucket (useful as a categorical predictor)
    df["power_tier"] = pd.cut(
        df["power_kw"],
        bins=[0, 3, 15, 50, 300],
        labels=["L1", "L2", "DC_Mid", "DC_High"],
    ).cat.codes.astype("int8")

    return df


def build_station_summary(hourly_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate hourly panel to per-station summary statistics."""
    summary = (
        hourly_df.groupby("station_id")
        .agg(
            mean_sessions=("sessions_per_hour", "mean"),
            std_sessions=("sessions_per_hour", "std"),
            mean_energy=("total_energy_kwh", "mean"),
            total_sessions=("sessions_per_hour", "sum"),
            mean_utilization=("utilization_rate", "mean"),
            peak_utilization=("utilization_rate", "max"),
            station_type=("station_type", "first"),
            location_type=("location_type", "first"),
            connector_type=("connector_type", "first") if "connector_type" in hourly_df.columns else ("station_type", "first"),
            power_kw=("power_kw", "first"),
            num_ports=("num_ports", "first"),
            latitude=("latitude", "first"),
            longitude=("longitude", "first"),
            region=("region", "first"),
        )
        .reset_index()
    )

    from voltiq.config.settings import settings

    summary["utilization_class"] = pd.cut(
        summary["mean_utilization"],
        bins=[0, settings.low_utilization_threshold, settings.high_utilization_threshold, 1.01],
        labels=["Low", "Medium", "High"],
    )

    return summary
