"""
Geocodes street addresses to (lat, lon) using geopy's ArcGIS backend.
All results are cached locally so each unique address is only looked up once.
"""
import json
import time
from pathlib import Path

import pandas as pd
from geopy.geocoders import ArcGIS

from config.settings import CACHE_DIR

_GEOCODE_CACHE_PATH = CACHE_DIR / "geocode_cache.json"
_geolocator = ArcGIS(timeout=10)


def _load_cache() -> dict:
    if _GEOCODE_CACHE_PATH.exists():
        try:
            with open(_GEOCODE_CACHE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            _GEOCODE_CACHE_PATH.unlink(missing_ok=True)
    return {}


def _save_cache(cache: dict):
    _GEOCODE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_GEOCODE_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def geocode_address(address: str) -> tuple[float | None, float | None]:
    """Return (lat, lon) for an address string, using cache when available."""
    if not address or not str(address).strip():
        return None, None

    address = str(address).strip()
    if address.lower() in ("nan", "none", "null", "n/a", "na"):
        return None, None
    cache = _load_cache()

    if address in cache:
        entry = cache[address]
        return entry["lat"], entry["lon"]

    try:
        time.sleep(0.5)  # respect ArcGIS public endpoint rate limit
        location = _geolocator.geocode(address)
        if location:
            lat, lon = location.latitude, location.longitude
            cache[address] = {"lat": lat, "lon": lon}
            _save_cache(cache)
            return lat, lon
    except Exception:
        pass

    return None, None


def geocode_dataframe(df: pd.DataFrame, address_col: str = "address") -> pd.DataFrame:
    """
    Add 'lat' and 'lon' columns to df by geocoding address_col.
    Rows that already have valid lat/lon are skipped.
    """
    df = df.copy()
    if "lat" not in df.columns:
        df["lat"] = None
    if "lon" not in df.columns:
        df["lon"] = None

    for idx, row in df.iterrows():
        if pd.notna(row.get("lat")) and pd.notna(row.get("lon")):
            continue
        addr = row.get(address_col, "")
        lat, lon = geocode_address(addr)
        df.at[idx, "lat"] = lat
        df.at[idx, "lon"] = lon

    return df
