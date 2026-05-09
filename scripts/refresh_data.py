"""
Standalone script to manually refresh the local JSON cache from Google Sheets.

Usage:
    python scripts/refresh_data.py
    python scripts/refresh_data.py --geocode   # also geocode any missing lat/lon
"""
import sys
import argparse
from pathlib import Path

# Make sure project root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.data_loader import load_resources, load_map_data
from config.settings import CACHE_DIR


def main():
    parser = argparse.ArgumentParser(description="Refresh Utah Startup Hub data cache")
    parser.add_argument(
        "--geocode",
        action="store_true",
        help="Geocode any map entries that are missing lat/lon",
    )
    args = parser.parse_args()

    print("━" * 50)
    print("  Utah Startup Hub — Data Refresh")
    print("━" * 50)

    # ── Resources ─────────────────────────────────────────────────────────────
    print("\n📋 Refreshing resources from Google Sheets…")
    df_resources = load_resources(force_refresh=True)
    if df_resources.empty:
        print("  ⚠  Could not fetch resources. Cache preserved if it existed.")
    else:
        print(f"  ✓  {len(df_resources)} rows cached → {CACHE_DIR / 'resources.json'}")

    # ── Map data ──────────────────────────────────────────────────────────────
    print("\n🗺️  Refreshing map data from Google Sheets…")
    df_map = load_map_data(force_refresh=True)
    if df_map.empty:
        print("  ⚠  Could not fetch map data. Cache preserved if it existed.")
    else:
        print(f"  ✓  {len(df_map)} rows cached → {CACHE_DIR / 'map_data.json'}")

    # ── Optional geocoding pass ────────────────────────────────────────────────
    if args.geocode and not df_map.empty:
        from modules.geocoder import geocode_dataframe
        import pandas as pd
        import json

        print("\n📍 Geocoding missing coordinates…")
        addr_col = None
        for c in df_map.columns:
            if c.lower().strip() in ("address", "full address", "location"):
                addr_col = c
                break

        if addr_col:
            df_map = geocode_dataframe(df_map, addr_col)
            cache_path = CACHE_DIR / "map_data.json"
            df_map.to_json(cache_path, orient="records", indent=2, force_ascii=False)
            found = df_map["lat"].notna().sum()
            print(f"  ✓  {found}/{len(df_map)} rows now have coordinates")
        else:
            print("  ⚠  Could not find an address column in the map sheet.")

    print("\n✅ Done!\n")


if __name__ == "__main__":
    main()
