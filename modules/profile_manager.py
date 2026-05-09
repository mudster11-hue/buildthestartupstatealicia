"""
Stores and retrieves entrepreneur profiles and saved-item lists as JSON files.
Each entrepreneur's profile lives at  data/profiles/{user_id}.json
Saved grant IDs live at               data/saved/{user_id}_grants.json
Saved startup IDs live at             data/saved/{investor_id}_startups.json
"""
import json
import base64
import io
from datetime import datetime
from pathlib import Path

from PIL import Image

from config.settings import PROFILES_DIR, SAVED_DIR


# ── Helpers ───────────────────────────────────────────────────────────────────

def _profile_path(user_id: str) -> Path:
    return PROFILES_DIR / f"{user_id}.json"


def _saved_path(user_id: str, kind: str) -> Path:
    return SAVED_DIR / f"{user_id}_{kind}.json"


def _read_json(path: Path, default):
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Profiles ──────────────────────────────────────────────────────────────────

def save_profile(user_id: str, profile_data: dict):
    data = {**profile_data, "user_id": user_id, "updated_at": datetime.now().isoformat()}
    _write_json(_profile_path(user_id), data)


def load_profile(user_id: str) -> dict:
    return _read_json(_profile_path(user_id), {})


def get_all_public_profiles() -> list[dict]:
    """Return profiles where the entrepreneur opted in to the investor map."""
    if not PROFILES_DIR.exists():
        return []
    profiles = []
    for path in PROFILES_DIR.glob("*.json"):
        p = _read_json(path, {})
        if p.get("open_to_investors"):
            profiles.append(p)
    return profiles


# ── Logo handling ─────────────────────────────────────────────────────────────

def encode_logo(uploaded_file) -> str | None:
    """Convert an uploaded image to a base64 data-URI for inline embedding."""
    if uploaded_file is None:
        return None
    try:
        img = Image.open(uploaded_file).convert("RGBA")
        img.thumbnail((120, 120), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{b64}"
    except Exception:
        return None


# ── Saved grants (entrepreneur) ───────────────────────────────────────────────

def load_saved_grants(user_id: str) -> list:
    return _read_json(_saved_path(user_id, "grants"), [])


def toggle_saved_grant(user_id: str, grant_id: str):
    saved = load_saved_grants(user_id)
    if grant_id in saved:
        saved.remove(grant_id)
    else:
        saved.append(grant_id)
    _write_json(_saved_path(user_id, "grants"), saved)


# ── Saved startups (investor) ─────────────────────────────────────────────────

def load_saved_startups(investor_id: str) -> list:
    return _read_json(_saved_path(investor_id, "startups"), [])


def toggle_saved_startup(investor_id: str, startup_id: str):
    saved = load_saved_startups(investor_id)
    if startup_id in saved:
        saved.remove(startup_id)
    else:
        saved.append(startup_id)
    _write_json(_saved_path(investor_id, "startups"), saved)
