"""Full training pipeline — generates data, engineers features, trains all models, saves artifacts."""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Allow running as `python scripts/train.py` from project root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voltiq.config.settings import settings
from voltiq.data import clean_sessions, load_raw_data
from voltiq.evaluation.comparison import compare_classification_models, compare_regression_models
from voltiq.evaluation.fairness import fairness_check_regression, underserved_stations
from voltiq.features import (
    add_lag_features,
    add_rolling_features,
    add_station_features,
    add_temporal_features,
    build_hourly_aggregate,
    build_station_summary,
)
from voltiq.models.registry import save_model
from voltiq.utils.logging import configure_logging, get_logger
from voltiq.utils.seed import set_global_seed

configure_logging(settings.log_level)
logger = get_logger("train")


def _save_df(df: "pd.DataFrame", path: Path, fmt: str = "csv") -> None:  # type: ignore[name-defined]
    """Save DataFrame to CSV (default) or parquet with fastparquet engine."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "csv":
        df.to_csv(str(path), index=False)
    else:
        df.to_parquet(str(path), index=False, engine="fastparquet")


def main() -> None:
    import pandas as pd

    set_global_seed(settings.random_seed)
    logger.info("Pipeline start", data_source=settings.data_source)

    # ── 1. Load & clean ──────────────────────────────────────────────────────
    sessions_raw, stations_df = load_raw_data(force_regenerate=False)
    sessions = clean_sessions(sessions_raw)
    logger.info("Sessions cleaned", n=len(sessions))

    settings.data_interim_dir.mkdir(parents=True, exist_ok=True)
    _save_df(sessions, settings.data_interim_dir / "sessions_clean.csv")

    # ── 2. Feature engineering ───────────────────────────────────────────────
    sessions = add_temporal_features(sessions)
    sessions = add_station_features(sessions)

    hourly = build_hourly_aggregate(sessions)
    hourly = add_temporal_features(hourly, timestamp_col="hour_bucket")
    hourly = add_station_features(hourly)
    hourly = add_lag_features(hourly)
    hourly = add_rolling_features(hourly)

    settings.data_processed_dir.mkdir(parents=True, exist_ok=True)
    _save_df(hourly, settings.data_processed_dir / "hourly_features.csv")

    station_summary = build_station_summary(hourly)
    station_summary = add_station_features(station_summary)
    _save_df(station_summary, settings.data_processed_dir / "station_summary.csv")
    _save_df(stations_df, settings.data_processed_dir / "stations.csv")

    logger.info("Feature engineering complete", hourly_rows=len(hourly), stations=len(station_summary))

    # ── 3. Regression model comparison ───────────────────────────────────────
    reg_results, best_reg_model, best_reg_name, reg_features, X_train, X_test, y_train, y_test = (
        compare_regression_models(hourly)
    )
    save_model(
        best_reg_model,
        best_reg_name,
        reg_results[0],
        reg_features,
        model_type="regression",
    )

    # ── 4. Fairness check ────────────────────────────────────────────────────
    if best_reg_model is not None and len(X_test) > 0:
        y_pred_test = best_reg_model.predict(X_test)
        test_df = hourly.loc[X_test.index] if hasattr(X_test, "index") else hourly.tail(len(X_test))
        fairness = fairness_check_regression(test_df.reset_index(drop=True), y_pred_test, y_test.values)
    else:
        fairness = {}

    # ── 5. Classification model comparison ───────────────────────────────────
    clf_results, best_clf_model, best_clf_name, le, clf_features = compare_classification_models(
        station_summary
    )
    if best_clf_model is not None:
        save_model(
            best_clf_model,
            best_clf_name,
            clf_results[0] if clf_results else {},
            clf_features,
            model_type="classification",
        )

    # ── 6. Underserved stations ──────────────────────────────────────────────
    underserved = underserved_stations(station_summary)
    _save_df(underserved, settings.data_processed_dir / "underserved.csv")

    # ── 7. Write summary metrics ─────────────────────────────────────────────
    summary = {
        "regression_leaderboard": reg_results,
        "classification_leaderboard": clf_results,
        "fairness_by_location": fairness,
        "underserved_count": len(underserved),
        "total_sessions": len(sessions),
        "total_stations": len(station_summary),
    }
    settings.models_store_dir.mkdir(parents=True, exist_ok=True)
    summary_path = settings.models_store_dir / "pipeline_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    logger.info("Pipeline complete", summary_path=str(summary_path))
    print("\n[OK] Training pipeline complete. Summary:")
    print(json.dumps({"best_regression": best_reg_name, "best_classification": best_clf_name, **reg_results[0]}, indent=2, default=str))


if __name__ == "__main__":
    main()
