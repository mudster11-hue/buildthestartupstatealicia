# Utah Startup Hub

A demo-ready Streamlit web app that connects Utah entrepreneurs with grants/resources and investors with startups — all on an interactive map.

---

## What It Does

| Role | Features |
|---|---|
| **Entrepreneur** | Guided grant-finder quiz (≤6 questions), filtered resource cards, save favourites, startup profile builder, opt-in investor map pin, real-time messaging |
| **Investor** | Interactive Utah heat map (color = stage, size = employees), hover & click popups, save startups, direct messaging |

---

## Quick Start

### 1 — Clone / open the folder

```
C:\Users\mudst\startup_hub\
```

### 2 — Create a virtual environment (recommended)

```powershell
cd C:\Users\mudst\startup_hub
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3 — Install dependencies

```powershell
pip install -r requirements.txt
```

### 4 — Run the app

```powershell
streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.

> **Demo mode:** No login needed. Click "I'm an Entrepreneur" or "I'm an Investor" on the landing page.

---

## Folder Structure

```
startup_hub/
│
├── app.py                  ← Main entry point (router + nav)
├── requirements.txt
├── README.md
│
├── .streamlit/
│   └── config.toml         ← Theme colours
│
├── config/
│   └── settings.py         ← All constants: URLs, stages, colours, demo users
│
├── data/
│   ├── raw/                ← Downloaded CSV files (auto-created)
│   ├── cache/              ← JSON cache (resources, map, geocode, sample startups)
│   ├── profiles/           ← One JSON file per entrepreneur profile
│   ├── saved/              ← Saved grants (per entrepreneur) + saved startups (per investor)
│   └── messages/           ← One JSON file per conversation thread
│
├── modules/                ← Business logic (no Streamlit UI here)
│   ├── auth.py             ← Demo session management
│   ├── data_loader.py      ← Google Sheets → JSON cache
│   ├── geocoder.py         ← Address → lat/lon via geopy ArcGIS (free)
│   ├── questionnaire.py    ← Builds questions from the resource data columns
│   ├── resource_filter.py  ← Filters resources based on questionnaire answers
│   ├── profile_manager.py  ← Save/load entrepreneur profiles + logo encoding
│   └── messaging.py        ← Thread-based messaging (JSON files)
│
├── scripts/
│   └── refresh_data.py     ← CLI: force-refresh the Google Sheets cache
│
└── views/                  ← Streamlit UI pages
    ├── landing.py          ← Role selector
    ├── entrepreneur/
    │   ├── dashboard.py    ← Home with stats + quick actions
    │   ├── quiz.py         ← Step-by-step grant finder
    │   ├── resources.py    ← Resource cards with save toggle
    │   ├── profile.py      ← Profile form + map opt-in
    │   └── messages.py     ← Inbox (receives messages from investors)
    └── investor/
        ├── map_view.py     ← Folium heat map of Utah startups
        ├── dashboard.py    ← Saved startups list
        └── messages.py     ← Send & manage messages to founders
```

---

## Data Sources

| Source | URL | Cached at |
|---|---|---|
| Resources / Grants | `RESOURCES_URL` in `config/settings.py` | `data/cache/resources.json` |
| Startup Map (read-only) | `MAP_URL` in `config/settings.py` | `data/cache/map_data.json` |
| Demo startups | bundled | `data/cache/sample_startups.json` |
| Geocode results | geopy ArcGIS | `data/cache/geocode_cache.json` |

The cache refreshes automatically when it is older than **60 minutes** (configurable via `CACHE_TTL_MINUTES` in `config/settings.py`). The app always serves from the cache immediately so load times stay fast.

### Manual refresh

```powershell
python scripts/refresh_data.py          # refresh both sheets
python scripts/refresh_data.py --geocode  # also fill in missing lat/lon
```

---

## Address Format

For geocoding to work correctly, enter addresses in Utah's Plat System format:

```
123 W 4500 S, Sandy, UT 84070
67 W 13490 S, Draper, UT 84020
850 W 200 S, Salt Lake City, UT 84101
```

> **Why this format?** The ArcGIS geocoder understands Utah's grid system when the address uses this pattern: `[number] [direction] [street number] [direction], [City], UT [zip]`

---

## Investor Map

The heat map merges three sources:

1. **Demo startups** — 12 pre-seeded Utah companies with pre-calculated lat/lon (loads instantly).
2. **Entrepreneur profiles** — any entrepreneur who toggled "Open my profile to investors" in their profile.
3. **Google Sheets map data** — the `MAP_URL` sheet (if columns can be detected).

**Colour = Stage:**
| Colour | Stage |
|---|---|
| 🟣 Purple | Pre-Seed |
| 🔵 Blue | Seed |
| 🟢 Green | Early |
| 🟠 Orange | Growth |
| 🔴 Red | Maturity |

**Dot size = Number of Employees** (larger = more employees)

---

## Geocoding Note

This app uses **geopy's ArcGIS backend** — it calls ArcGIS's *free public endpoint* with no API key required. It is rate-limited to ~1 request/second and caches every result locally so each unique address is only looked up once.

If you later need higher throughput or SLA guarantees you can swap in the full ArcGIS API by replacing the `ArcGIS()` call in `modules/geocoder.py` with:

```python
from geopy.geocoders import ArcGIS
_geolocator = ArcGIS(username="YOUR_USER", password="YOUR_PASS", referer="YOUR_APP")
```

---

## Configuration

All constants live in `config/settings.py`. Things you may want to change:

| Setting | Purpose |
|---|---|
| `RESOURCES_URL` | Google Sheets export URL for grants/resources |
| `MAP_URL` | Google Sheets export URL for existing startup map data |
| `CACHE_TTL_MINUTES` | How often to check for sheet updates (default 60) |
| `DEMO_USERS` | Names/emails shown in demo mode |
| `STAGE_OPTIONS` | Stage labels and descriptions |
| `BUSINESS_TYPES` | Business type labels and descriptions |
| `STAGE_COLORS` | Map dot colours per stage |
| `EMPLOYEE_RADIUS` | Map dot radius per employee band |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Map shows blank | Check internet; the first load geocodes addresses (takes a few seconds). Demo startups should always show. |
| "Could not load resources" | The Google Sheet may be private. Make sure the share link is set to "Anyone with the link can view". |
| Geocoding returns None | Verify address format (see above). Run `python scripts/refresh_data.py --geocode` after fixing addresses. |
| App won't start | Run `pip install -r requirements.txt` and make sure Python ≥ 3.10 |

---

## Tech Stack

| Library | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `pandas` | Data loading & manipulation |
| `folium` + `streamlit-folium` | Interactive Leaflet map |
| `geopy` | Address geocoding (ArcGIS backend) |
| `Pillow` | Logo image resizing & base64 encoding |
| `requests` | Fetching Google Sheets CSV exports |

---

*Built for demo purposes. All data stored locally in the `data/` directory.*
