"""Model registry: versioned save/load with metadata."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib

from voltiq.config.settings import settings
from voltiq.utils.logging import get_logger

logger = get_logger(__name__)


def save_model(
    model: Any,
    model_name: str,
    metrics: dict[str, Any],
    feature_cols: list[str],
    model_type: str = "regression",
) -> Path:
    """Serialize model and write versioned metadata JSON to models_store/."""
    store = settings.models_store_dir
    store.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    model_filename = f"{model_type}_{model_name}_{timestamp}.joblib"
    meta_filename = f"{model_type}_{model_name}_{timestamp}_meta.json"

    model_path = store / model_filename
    meta_path = store / meta_filename

    joblib.dump(model, model_path, compress=3)

    metadata = {
        "model_name": model_name,
        "model_type": model_type,
        "timestamp": timestamp,
        "metrics": metrics,
        "feature_cols": feature_cols,
        "model_file": model_filename,
    }
    meta_path.write_text(json.dumps(metadata, indent=2))

    # Overwrite the "latest" symlink-equivalent (a fixed-name file)
    latest_meta = store / f"{model_type}_latest_meta.json"
    latest_meta.write_text(json.dumps(metadata, indent=2))
    latest_model = store / f"{model_type}_latest.joblib"
    joblib.dump(model, latest_model, compress=3)

    logger.info("Model saved", model=model_name, path=str(model_path))
    return model_path


def load_latest_model(model_type: str = "regression") -> tuple[Any, dict[str, Any]]:
    """Load the most recently saved model of the given type."""
    store = settings.models_store_dir
    latest_meta = store / f"{model_type}_latest_meta.json"
    latest_model = store / f"{model_type}_latest.joblib"

    if not latest_model.exists():
        raise FileNotFoundError(f"No saved {model_type} model found in {store}")

    model = joblib.load(latest_model)
    metadata = json.loads(latest_meta.read_text())
    logger.info("Model loaded", model_type=model_type, model_name=metadata.get("model_name"))
    return model, metadata


def list_saved_models() -> list[dict[str, Any]]:
    """Return metadata for all saved models in the store."""
    store = settings.models_store_dir
    if not store.exists():
        return []
    meta_files = sorted(store.glob("*_meta.json"), reverse=True)
    results = []
    for f in meta_files:
        try:
            results.append(json.loads(f.read_text()))
        except json.JSONDecodeError:
            continue
    return results
