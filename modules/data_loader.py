"""
Loads data from Google Sheets and caches it locally as JSON.
On startup the cache is used immediately; a background-friendly refresh
runs if the cache is older than CACHE_TTL_MINUTES.
"""
import json
import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from pathlib import Path

from config.settings import (
    RESOURCES_URL,
    MAP_URL,
    CACHE_TTL_MINUTES,
    CACHE_DIR,
    RAW_DIR,
)


def _cache_is_stale(path: Path) -> bool:
    if not path.exists():
        return True
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    return age > timedelta(minutes=CACHE_TTL_MINUTES)


def _fetch_csv(url: str) -> pd.DataFrame:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return pd.read_csv(StringIO(resp.text))


def _save_json(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(path, orient="records", indent=2, force_ascii=False)


def _load_json(path: Path) -> pd.DataFrame:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)


# ── Public API ────────────────────────────────────────────────────────────────

def load_resources(force_refresh: bool = False) -> pd.DataFrame:
    cache_path = CACHE_DIR / "resources.json"

    if force_refresh or _cache_is_stale(cache_path):
        try:
            df = _fetch_csv(RESOURCES_URL)
            _save_json(df, cache_path)
            # also keep a raw CSV copy
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(RAW_DIR / "resources.csv", index=False)
        except Exception:
            pass  # fall through to cached version below

    if cache_path.exists():
        return _load_json(cache_path)
    return pd.DataFrame()


def load_map_data(force_refresh: bool = False) -> pd.DataFrame:
    cache_path = CACHE_DIR / "map_data.json"

    if force_refresh or _cache_is_stale(cache_path):
        try:
            df = _fetch_csv(MAP_URL)
            _save_json(df, cache_path)
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(RAW_DIR / "map_data.csv", index=False)
        except Exception:
            pass

    if cache_path.exists():
        return _load_json(cache_path)
    return pd.DataFrame()


def last_refresh_time(source: str = "resources") -> str | None:
    path = CACHE_DIR / f"{source}.json"
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return mtime.strftime("%b %d, %Y at %I:%M %p")
