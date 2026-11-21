"""IO utilities — Parquet read/write using fastparquet to avoid pyarrow DLL issues."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


PARQUET_ENGINE = "fastparquet"


def read_parquet(path: str | Path) -> pd.DataFrame:
    try:
        return pd.read_parquet(str(path), engine=PARQUET_ENGINE)
    except Exception:
        return pd.read_parquet(str(path))


def write_parquet(df: pd.DataFrame, path: str | Path, index: bool = False) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(str(path), engine=PARQUET_ENGINE, index=index)
    except Exception:
        df.to_parquet(str(path), index=index)
