import json
from pathlib import Path


def load_dataset(source_dataset: str, config_path: str = None):
    if config_path is None:
        raise SystemExit("load_dataset requires source_dir or config_path.")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"Failed to load config from '{config_path}': {e}") from e

    source_dir = config.get("source_datasets")
    if not source_dir:
        raise SystemExit(f"Config at '{config_path}' missing 'source_datasets' key.")

    path = Path(source_dir) / f"{source_dataset}.json"
    if not path.is_file():
        raise SystemExit(f"Dataset file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse dataset JSON at {path}: {exc}")
