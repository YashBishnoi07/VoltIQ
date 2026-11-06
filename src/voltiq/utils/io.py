"""IO utilities — Parquet read/write using fastparquet to avoid pyarrow DLL issues."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


PARQUET_ENGINE = "fastparquet"


def read_parquet(path: str | Path) -> pd.DataFrame:
    return pd.read_parquet(str(path), engine=PARQUET_ENGINE)


def write_parquet(df: pd.DataFrame, path: str | Path, index: bool = False) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(str(path), engine=PARQUET_ENGINE, index=index)
