import pandas as pd
import numpy as np
from voltiq.data.cleaning import clean_sessions
from voltiq.data.anonymization import anonymize


def test_clean_sessions_drops_duplicates():
    df = pd.DataFrame({
        "session_id": ["S1", "S1"],
        "station_id": ["STN-1", "STN-1"],
        "user_id": ["U1", "U1"],
        "start_time": ["2024-01-01 10:00:00", "2024-01-01 10:00:00"],
        "end_time": ["2024-01-01 12:00:00", "2024-01-01 12:00:00"],
        "duration_hours": [2.0, 2.0],
        "energy_kwh": [15.0, 15.0],
        "power_kw": [7.0, 7.0],
        "station_type": ["L2", "L2"],
        "latitude": [37.77, 37.77],
        "longitude": [-122.41, -122.41],
    })
    cleaned = clean_sessions(df)
    assert len(cleaned) == 1


def test_clean_sessions_imputes_missing_energy():
    df = pd.DataFrame({
        "session_id": ["S1", "S2"],
        "station_id": ["STN-1", "STN-2"],
        "user_id": ["U1", "U2"],
        "start_time": ["2024-01-01 10:00:00", "2024-01-01 11:00:00"],
        "end_time": ["2024-01-01 12:00:00", "2024-01-01 13:00:00"],
        "duration_hours": [2.0, 2.0],
        "energy_kwh": [20.0, np.nan],
        "power_kw": [10.0, 10.0],
        "station_type": ["L2", "L2"],
        "latitude": [37.77, 37.77],
        "longitude": [-122.41, -122.41],
    })
    cleaned = clean_sessions(df)
    assert not cleaned["energy_kwh"].isna().any()
    assert cleaned.loc[cleaned["session_id"] == "S2", "energy_kwh"].iloc[0] == 20.0


def test_anonymize_hashes_user_ids():
    df = pd.DataFrame({
        "user_id": ["real_user_name", "12345"],
        "home_address": ["123 Elm St", "456 Oak St"],
    })
    anon = anonymize(df)
    assert "home_address" not in anon.columns
    assert anon["user_id"].iloc[0] != "real_user_name"
    assert len(anon["user_id"].iloc[0]) == 16
