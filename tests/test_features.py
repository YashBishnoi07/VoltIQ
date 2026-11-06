import pandas as pd
from voltiq.features.temporal import add_temporal_features
from voltiq.features.station import add_station_features


def test_add_temporal_features():
    df = pd.DataFrame({
        "start_time": pd.to_datetime(["2024-01-01 08:30:00", "2024-01-06 14:00:00"]),
    })
    res = add_temporal_features(df, "start_time")
    assert "hour" in res.columns
    assert "is_weekend" in res.columns
    assert "hour_sin" in res.columns
    assert "hour_cos" in res.columns
    assert res["is_weekend"].iloc[0] == 0  # Monday
    assert res["is_weekend"].iloc[1] == 1  # Saturday
    assert res["is_peak_hour"].iloc[0] == 1  # 8am is peak


def test_add_station_features():
    df = pd.DataFrame({
        "station_type": ["L1", "L2", "DC_Fast"],
        "location_type": ["rural", "suburban", "urban"],
        "power_kw": [1.5, 7.2, 100.0],
    })
    res = add_station_features(df)
    assert "station_type_enc" in res.columns
    assert res["station_type_enc"].tolist() == [0, 1, 2]
    assert "power_tier" in res.columns
