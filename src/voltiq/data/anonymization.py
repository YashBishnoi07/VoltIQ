"""Anonymization utilities — hash user/vehicle IDs, strip PII."""
from __future__ import annotations

import hashlib

import pandas as pd


def anonymize(df: pd.DataFrame, salt: str = "voltiq-v1") -> pd.DataFrame:
    """Hash PII columns in-place and return the sanitised DataFrame."""
    df = df.copy()
    if "user_id" in df.columns:
        df["user_id"] = df["user_id"].apply(lambda uid: _sha256(str(uid), salt))
    # Drop any columns that contain raw home coordinates if they were added upstream
    pii_cols = {"home_lat", "home_lon", "home_address", "vehicle_vin"}
    df = df.drop(columns=[c for c in pii_cols if c in df.columns])
    return df


def _sha256(value: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:16]
