"""
Investor map view — pydeck map, inline filter panel, kanban list.
Filters live beside the map (not in the sidebar).
"""
import json

import pandas as pd
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components

from config.settings import CACHE_DIR, DATA_DIR
from modules.geocoder import geocode_dataframe
from modules.profile_manager import (
    get_all_public_profiles,
    load_saved_startups,
    toggle_saved_startup,
)

_PROCESSED_PATH = DATA_DIR / "processed_data.json"
_LAYER_ID = "startup-layer"

_SECTION_COLORS: dict[str, list[int]] = {
    "B2B Software":     [ 33, 150, 243],
    "Consumer":         [ 76, 175,  80],
    "Security":         [244,  67,  54],
    "Bio/Medical Tech": [156,  39, 176],
    "FinTech":          [255, 152,   0],
    "Energy":           [  0, 188, 212],
    "Marketplaces":     [233,  30,  99],
}
_DEFAULT_COLOR = [149, 165, 166]

_STAGE_ORDER = [
    "Pre-Seed", "Seed",
    "Series A", "Series B", "Series C", "Series D+",
    "Bootstrapped",
]
_BAD = {"nan", "none", "null", "n/a", ""}


# ── Data ──────────────────────────────────────────────────────────────────────

def _load_processed_data() -> pd.DataFrame:
    if not _PROCESSED_PATH.exists():
        return pd.DataFrame()
    with open(_PROCESSED_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    rows = []
    for addr_key, entry in raw.items():
        info = entry.get("info", {})
        rows.append({
            "id":           addr_key,
            "startup_name": str(info.get("Startup Name ", "") or info.get("Startup Name", "")).strip(),
            "description":  str(info.get("Description of startup", "")).strip(),
            "address":      str(info.get("Full Address", addr_key)).strip(),
            "stage":        str(info.get("Stage", "")).strip().rstrip(". "),
            "employees":    str(info.get("# of Employees ", "") or info.get("# of Employees", "")).strip(),
            "section":      str(info.get("Section", "")).strip().rstrip(". "),
            "website":      str(info.get("Website", "")).strip(),
            "lat":          entry.get("lat"),
            "lon":          entry.get("lon"),
        })
    return pd.DataFrame(rows)


def _load_map_cache_fallback() -> pd.DataFrame:
    cache_path = CACHE_DIR / "map_data.json"
    if not cache_path.exists():
        return pd.DataFrame()
    with open(cache_path, encoding="utf-8") as f:
        raw = json.load(f)
    rows = []
    for entry in raw:
        addr = str(entry.get("Full Address", "") or "").strip()
        rows.append({
            "id":           addr or str(entry.get("Startup Name ", "")),
            "startup_name": str(entry.get("Startup Name ", "") or entry.get("Startup Name", "")).strip(),
            "description":  str(entry.get("Description of startup", "")).strip(),
            "address":      addr,
            "stage":        str(entry.get("Stage", "")).strip().rstrip(". "),
            "employees":    str(entry.get("# of Employees ", "") or entry.get("# of Employees", "")).strip(),
            "section":      str(entry.get("Section", "")).strip().rstrip(". "),
            "website":      str(entry.get("Website", "")).strip(),
            "lat":          None,
            "lon":          None,
        })
    df = pd.DataFrame(rows)
    # Only geocode rows with real addresses (blank/nan addresses stay as None)
    has_addr = df["address"].apply(lambda a: bool(a) and a.lower() not in _BAD)
    if has_addr.any():
        geocoded = geocode_dataframe(df[has_addr].copy(), "address")
        df.loc[has_addr, "lat"] = geocoded["lat"].values
        df.loc[has_addr, "lon"] = geocoded["lon"].values
    return df


def _emp_to_radius(emp: str) -> float:
    if not emp or emp.lower() in _BAD:
        return 300.0
    s = emp.replace("+", "").replace(",", "").lower()
    if "-" in s:
        s = s.split("-")[-1].strip()
    mult = 1000 if "k" in s else 1
    s = s.replace("k", "").strip()
    try:
        return 250.0 + float(s) * mult
    except (ValueError, TypeError):
        return 300.0


def _add_display_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["fill_color"] = df["section"].map(lambda s: _SECTION_COLORS.get(s, _DEFAULT_COLOR))
    df["map_radius"] = df["employees"].apply(_emp_to_radius)
    return df


def _build_full_dataframe() -> pd.DataFrame:
    """Returns ALL startups including those without coordinates."""
    frames = []
    processed = _load_processed_data()
    if not processed.empty:
        frames.append(processed)
    else:
        cached = _load_map_cache_fallback()
        if not cached.empty:
            frames.append(cached)

    profiles = get_all_public_profiles()
    if profiles:
        pf = pd.DataFrame(profiles)
        pf["id"] = pf.get("user_id", pf.index.astype(str))
        for col in ["startup_name", "description", "address", "stage",
                    "employees", "section", "website", "lat", "lon"]:
            if col not in pf.columns:
                pf[col] = None
        frames.append(pf[["id", "startup_name", "description", "address",
                           "stage", "employees", "section", "website", "lat", "lon"]])

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.reset_index(drop=True)
    return _add_display_columns(combined)


# ── Logo helpers ──────────────────────────────────────────────────────────────

def _favicon_url(website: str) -> str | None:
    """Google favicon service — always returns an image, never a broken link."""
    if not website or str(website).lower() in _BAD:
        return None
    domain = str(website).strip()
    for prefix in ("https://", "http://", "www."):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
    domain = domain.split("/")[0].strip()
    if not domain or "." not in domain:
        return None
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"


def _logo_html(website: str, name: str, color: list[int], size: int = 32) -> str:
    """Logo div: Google favicon on top of a colored letter-avatar."""
    r, g, b = color
    initial = name[0].upper() if name else "?"
    favicon = _favicon_url(website)
    base_style = (
        f"width:{size}px;height:{size}px;border-radius:8px;flex-shrink:0;"
        f"display:flex;align-items:center;justify-content:center;"
    )
    avatar = (
        f"<div style='{base_style}background:rgb({r},{g},{b});"
        f"color:#fff;font-weight:700;font-size:{size // 2}px;'>"
        f"{initial}</div>"
    )
    if not favicon:
        return avatar
    return (
        f"<div style='position:relative;{base_style}'>"
        f"<div style='position:absolute;top:0;left:0;{base_style}"
        f"background:rgb({r},{g},{b});color:#fff;font-weight:700;"
        f"font-size:{size // 2}px;'>{initial}</div>"
        f"<img src='{favicon}' width='{size}' height='{size}' "
        f"style='position:absolute;top:0;left:0;border-radius:8px;"
        f"object-fit:contain;background:#fff;' "
        f"onerror=\"this.style.display='none'\">"
        f"</div>"
    )


# ── Filter helpers ────────────────────────────────────────────────────────────

def _all_stages(df: pd.DataFrame) -> list[str]:
    ordered = [s for s in _STAGE_ORDER if s in df["stage"].values]
    extra = sorted(s for s in df["stage"].unique()
                   if s and s.lower() not in _BAD and s not in _STAGE_ORDER)
    return ordered + extra


def _all_sections(df: pd.DataFrame) -> list[str]:
    return sorted(s for s in df["section"].unique() if s and s.lower() not in _BAD)


def _compute_filters(df: pd.DataFrame) -> tuple[set[str], set[str]]:
    """Read current checkbox state from session_state (no rendering)."""
    stage_sel = {s for s in _all_stages(df)
                 if st.session_state.get(f"chk_stage_{s}", True)}
    sect_sel  = {s for s in _all_sections(df)
                 if st.session_state.get(f"chk_section_{s}", True)}
    return stage_sel, sect_sel


def _render_filter_panel(df: pd.DataFrame):
    """Render checkboxes in the current column context."""
    st.markdown("#### Filters")

    st.markdown("**Stage**")
    cols = st.columns(2)
    for i, stage in enumerate(_all_stages(df)):
        cols[i % 2].checkbox(stage, value=True, key=f"chk_stage_{stage}")

    st.markdown("**Section**")
    for section in _all_sections(df):
        r, g, b = _SECTION_COLORS.get(section, _DEFAULT_COLOR)
        dot_col, chk_col = st.columns([0.1, 0.9])
        dot_col.markdown(
            f"<div style='width:10px;height:10px;border-radius:50%;"
            f"background:rgb({r},{g},{b});margin-top:7px;'></div>",
            unsafe_allow_html=True,
        )
        chk_col.checkbox(section, value=True, key=f"chk_section_{section}")

    pass


# ── Map ───────────────────────────────────────────────────────────────────────

def _render_map(plot_df: pd.DataFrame, render_key: int = 0) -> str | None:
    layer = pdk.Layer(
        "ScatterplotLayer",
        plot_df,
        id=_LAYER_ID,
        get_position="[lon, lat]",
        get_fill_color="fill_color",
        get_radius="map_radius",
        radius_min_pixels=5,
        radius_max_pixels=50,
        pickable=True,
        auto_highlight=True,
    )
    result = st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=pdk.ViewState(
                latitude=40.5723, longitude=-111.8597, zoom=9, pitch=0,
            ),
            map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
            tooltip={
                "html": (
                    "<div style='background:rgba(27,58,92,0.96);padding:10px 14px;"
                    "border-radius:8px;font-family:sans-serif;"
                    "border:1px solid rgba(255,255,255,0.15);'>"
                    "<strong style='color:#fff;font-size:.9rem;'>{startup_name}</strong><br>"
                    "<span style='color:#F5A623;font-size:.78rem;'>{stage}</span>"
                    "<span style='color:#aaa;font-size:.75rem;'> · {section}</span><br>"
                    "<span style='color:#888;font-size:.72rem;'>👥 {employees}</span><br>"
                    "<em style='color:#aaa;font-size:.7rem;'>Click to view &amp; save</em>"
                    "</div>"
                ),
                "style": {"backgroundColor": "transparent", "padding": "0"},
            },
        ),
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-object",
        key=f"map_chart_{render_key}",
    )
    try:
        objects = result.selection["objects"].get(_LAYER_ID, [])
        if objects:
            return objects[0].get("startup_name")
    except (KeyError, TypeError, AttributeError):
        pass
    return None


def _render_legend():
    swatches = "".join(
        f"<span style='margin-right:10px;white-space:nowrap;'>"
        f"<span style='display:inline-block;width:9px;height:9px;border-radius:50%;"
        f"background:rgb({c[0]},{c[1]},{c[2]});vertical-align:middle;margin-right:3px;'></span>"
        f"<span style='font-size:.73rem;color:#777;'>{sec}</span></span>"
        for sec, c in _SECTION_COLORS.items()
    )
    st.markdown(
        f"<div style='margin:.2rem 0 .5rem;line-height:2.2;'>{swatches}</div>",
        unsafe_allow_html=True,
    )


# ── Selection card ────────────────────────────────────────────────────────────

def _show_selection_card(row: pd.Series, investor_id: str):
    sid   = str(row.get("id", ""))
    name  = str(row.get("startup_name", "Unknown"))
    stage = str(row.get("stage", "") or "")
    sect  = str(row.get("section", "") or "")
    emp   = str(row.get("employees", "") or "")
    desc  = str(row.get("description", "") or "")
    site  = str(row.get("website", "") or "")
    is_saved = sid in _get_saved(investor_id)
    color = _SECTION_COLORS.get(sect, _DEFAULT_COLOR)
    r, g, b = color

    st.markdown(
        f"<div style='height:3px;background:linear-gradient("
        f"90deg,rgb({r},{g},{b}),rgba({r},{g},{b},0.2));"
        f"border-radius:2px;margin-bottom:10px;'></div>",
        unsafe_allow_html=True,
    )

    title_col, close_col = st.columns([8, 1])
    with title_col:
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:12px;'>"
            f"{_logo_html(site, name, color, 40)}"
            f"<div><strong style='font-size:1.05rem;'>{name}</strong><br>"
            f"<span style='color:#888;font-size:.8rem;'>"
            f"{'👥 ' + emp + ' employees' if emp not in ('nan','') else ''}"
            f"</span></div></div>",
            unsafe_allow_html=True,
        )
    if close_col.button("✕", key="card_close", help="Dismiss"):
        st.session_state.pop("map_selected_name", None)
        st.rerun()

    st.markdown("")
    info_col, action_col = st.columns([3, 1])
    with info_col:
        badge_s = (
            f"<span style='background:rgba(245,166,35,.15);color:#F5A623;"
            f"padding:3px 10px;border-radius:12px;font-size:.78rem;margin-right:6px;'>"
            f"{stage}</span>"
        )
        badge_t = (
            f"<span style='background:rgba({r},{g},{b},.12);color:rgb({r},{g},{b});"
            f"padding:3px 10px;border-radius:12px;font-size:.78rem;"
            f"border:1px solid rgba({r},{g},{b},.3);'>{sect}</span>"
        )
        st.markdown(badge_s + badge_t, unsafe_allow_html=True)
        st.markdown("")
        st.markdown(desc[:500] + ("…" if len(desc) > 500 else ""))

    with action_col:
        if st.button(
            "❤️ Saved" if is_saved else "🤍 Save",
            key=f"card_save_{sid}",
            use_container_width=True,
            type="secondary" if is_saved else "primary",
        ):
            _toggle_saved(investor_id, sid)
            st.rerun()
        if site and site.lower() not in _BAD:
            url = site if site.startswith("http") else f"https://{site}"
            st.link_button("🌐 Website", url, use_container_width=True)

    if site and site.lower() not in _BAD:
        st.markdown(
            "<div style='background:#FEF9E7;border-left:3px solid #F5A623;"
            "border-radius:0 6px 6px 0;padding:8px 12px;margin-top:6px;"
            "font-size:.78rem;color:#7D6608;'>"
            "💬 To get in touch, visit their website above for contact details."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='background:#F8F9FA;border-left:3px solid #CED4DA;"
            "border-radius:0 6px 6px 0;padding:8px 12px;margin-top:6px;"
            "font-size:.78rem;color:#6C757D;'>"
            "💬 No website listed — try searching for this company directly."
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")


# ── Saved-set helpers (session-state backed) ─────────────────────────────────

def _saved_key(investor_id: str) -> str:
    return f"_saved_set_{investor_id}"


def _get_saved(investor_id: str) -> set[str]:
    """Return the live saved-startup set for this session."""
    k = _saved_key(investor_id)
    if k not in st.session_state:
        st.session_state[k] = set(load_saved_startups(investor_id))
    return st.session_state[k]


def _toggle_saved(investor_id: str, sid: str):
    """Toggle a startup in the session-state set AND persist to disk."""
    saved = _get_saved(investor_id)
    if sid in saved:
        saved.discard(sid)
    else:
        saved.add(sid)
    # Persist to disk
    toggle_saved_startup(investor_id, sid)


# ── Unmapped startups ─────────────────────────────────────────────────────────

def _show_unmapped(unmapped_df: pd.DataFrame, investor_id: str):
    with st.expander(
        f"🏠 {len(unmapped_df)} startups don't have a listed address yet — click to view",
        expanded=False,
    ):
        cols = st.columns(3)
        for idx, (_, row) in enumerate(unmapped_df.reset_index(drop=True).iterrows()):
            with cols[idx % 3]:
                _kanban_card(row, "unmapped", idx, investor_id)


# ── Kanban list view ──────────────────────────────────────────────────────────

def _show_list_view(plot_df: pd.DataFrame, investor_id: str):
    hdr_col, toggle_col = st.columns([4, 1])
    hdr_col.markdown(f"### All Startups ({len(plot_df)})")
    group_by = toggle_col.radio(
        "View by",
        ["Section", "Stage"],
        horizontal=True,
        key="list_group_by",
        label_visibility="collapsed",
    )

    if group_by == "Section":
        group_keys = sorted(s for s in plot_df["section"].unique()
                            if s and s.lower() not in _BAD)
        def get_group(k): return plot_df[plot_df["section"] == k]
        def get_color(k): return _SECTION_COLORS.get(k, _DEFAULT_COLOR)
    else:
        group_keys = [s for s in _STAGE_ORDER if s in plot_df["stage"].values]
        group_keys += sorted(s for s in plot_df["stage"].unique()
                             if s and s.lower() not in _BAD and s not in _STAGE_ORDER)
        def get_group(k): return plot_df[plot_df["stage"] == k]
        def get_color(_): return _DEFAULT_COLOR

    active = [k for k in group_keys if not get_group(k).empty]
    if not active:
        st.info("No startups match the current filters.")
        return

    cols = st.columns(len(active))
    for col, key in zip(cols, active):
        group_df = get_group(key)
        r, g, b = get_color(key)
        with col:
            st.markdown(
                f"<div style='background:rgba({r},{g},{b},.1);"
                f"border-left:3px solid rgb({r},{g},{b});"
                f"padding:5px 8px;border-radius:0 6px 6px 0;margin-bottom:8px;'>"
                f"<strong style='font-size:.83rem;'>{key}</strong>"
                f"<span style='color:#999;font-size:.72rem;margin-left:6px;'>({len(group_df)})</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            for idx, (_, row) in enumerate(group_df.reset_index(drop=True).iterrows()):
                _kanban_card(row, key, idx, investor_id)


def _kanban_card(row: pd.Series, group_key: str, idx: int, investor_id: str):
    sid   = str(row.get("id", ""))
    name  = str(row.get("startup_name", "Unknown"))
    desc  = str(row.get("description", "") or "")
    site  = str(row.get("website", "") or "")
    sect  = str(row.get("section", "") or "")
    saved = _get_saved(investor_id)
    is_saved = sid in saved
    color = _SECTION_COLORS.get(sect, _DEFAULT_COLOR)
    logo  = _logo_html(site, name, color, size=28)
    url   = None
    if site and site.lower() not in _BAD:
        url = site if site.startswith("http") else f"https://{site}"
    # Sanitise key — slashes/spaces are fine in Streamlit but keep it clean
    safe_group = "".join(c if c.isalnum() else "_" for c in group_key)
    key_base = f"{safe_group}_{idx}"

    with st.container(border=True):
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:7px;margin-bottom:4px;'>"
            f"{logo}"
            f"<span style='font-weight:600;font-size:.82rem;line-height:1.25;'>{name}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if desc:
            st.markdown(
                f"<div style='font-size:.75rem;color:#666;line-height:1.4;"
                f"display:-webkit-box;-webkit-line-clamp:2;"
                f"-webkit-box-orient:vertical;overflow:hidden;"
                f"margin-bottom:5px;'>{desc[:180]}</div>",
                unsafe_allow_html=True,
            )
        save_col, link_col = st.columns(2)
        if save_col.button(
            "❤️" if is_saved else "🤍",
            key=f"ks_{key_base}",
            use_container_width=True,
            help="Unsave" if is_saved else "Save",
        ):
            _toggle_saved(investor_id, sid)
            st.rerun()
        if url:
            link_col.link_button("🌐", url, use_container_width=True)


# ── Saved startups tab ────────────────────────────────────────────────────────

def _show_saved_tab(df: pd.DataFrame, investor_id: str):
    saved = _get_saved(investor_id)
    if not saved:
        st.markdown(
            "<div style='background:#F8F9FA;border-radius:12px;padding:40px;text-align:center;"
            "margin-top:1rem;'>"
            "<div style='font-size:3rem;'>⭐</div>"
            "<h3 style='color:#1B3A5C;'>No saved startups yet</h3>"
            "<p style='color:#6C757D;'>Click a dot on the Map tab, then hit "
            "<strong>Save</strong> to bookmark it here.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    saved_df = df[df["id"].astype(str).isin(saved)].copy()
    if saved_df.empty:
        st.info("Your saved startups couldn't be matched to the current dataset.")
        return

    st.markdown(f"**{len(saved_df)} saved startups**")
    st.markdown("---")

    for idx, (_, row) in enumerate(saved_df.reset_index(drop=True).iterrows()):
        sid   = str(row.get("id", ""))
        name  = str(row.get("startup_name", "Unknown"))
        stage = str(row.get("stage", "") or "")
        sect  = str(row.get("section", "") or "")
        emp   = str(row.get("employees", "") or "")
        desc  = str(row.get("description", "") or "")
        site  = str(row.get("website", "") or "")
        color = _SECTION_COLORS.get(sect, _DEFAULT_COLOR)
        r, g, b = color
        url = (site if site.startswith("http") else f"https://{site}") if site and site.lower() not in _BAD else None

        with st.container(border=True):
            head_col, act_col = st.columns([4, 1])
            with head_col:
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:10px;margin-bottom:6px;'>"
                    f"{_logo_html(site, name, color, 36)}"
                    f"<div>"
                    f"<strong style='font-size:1rem;color:#1B3A5C;'>{name}</strong><br>"
                    f"<span style='background:rgba(245,166,35,.15);color:#F5A623;"
                    f"padding:2px 8px;border-radius:10px;font-size:.75rem;margin-right:5px;'>{stage}</span>"
                    f"<span style='background:rgba({r},{g},{b},.12);color:rgb({r},{g},{b});"
                    f"padding:2px 8px;border-radius:10px;font-size:.75rem;'>{sect}</span>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
                if emp and emp.lower() not in _BAD:
                    st.caption(f"👥 {emp} employees")
                if desc:
                    st.markdown(
                        f"<div style='font-size:.85rem;color:#555;line-height:1.5;"
                        f"margin-top:4px;'>{desc[:300]}{'…' if len(desc)>300 else ''}</div>",
                        unsafe_allow_html=True,
                    )
            with act_col:
                if st.button("💔 Unsave", key=f"unsave_tab_{sid}_{idx}", use_container_width=True):
                    _toggle_saved(investor_id, sid)
                    st.rerun()
                if url:
                    st.link_button("🌐 Website", url, use_container_width=True)
                st.markdown(
                    "<div style='background:#FEF9E7;border-radius:6px;padding:7px 10px;"
                    "font-size:.72rem;color:#7D6608;margin-top:4px;text-align:center;'>"
                    "💬 Contact via website"
                    "</div>" if url else
                    "<div style='background:#F8F9FA;border-radius:6px;padding:7px 10px;"
                    "font-size:.72rem;color:#6C757D;margin-top:4px;text-align:center;'>"
                    "💬 No website listed"
                    "</div>",
                    unsafe_allow_html=True,
                )


# ── Entry point ───────────────────────────────────────────────────────────────

def show_investor_map(user: dict):
    if "map_df" not in st.session_state:
        with st.spinner("Loading startup data…"):
            st.session_state.map_df = _build_full_dataframe()

    df = st.session_state.map_df
    if df.empty:
        st.warning("No startup data found. Run `sync.py` to populate the map.")
        return

    # ── Tab bar (session-state driven so active tab survives reruns) ──────────
    if "investor_tab" not in st.session_state:
        st.session_state.investor_tab = "map"

    saved_count = len(_get_saved(user["id"]))
    saved_label = f"⭐  Saved ({saved_count})" if saved_count else "⭐  Saved"

    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0F2540 0%, #1B3A5C 50%, #1E4A78 100%);
            border-radius: 18px; padding: 36px 40px; margin-bottom: 1.5rem;
            border: 1px solid rgba(245,166,35,0.18);
            box-shadow: 0 8px 32px rgba(15,37,64,0.18);
            position: relative; overflow: hidden;
        ">
            <div style="position:absolute;top:0;left:0;right:0;height:3px;
                background:linear-gradient(90deg,#F5A623,#FFBC46,transparent);
                border-radius:18px 18px 0 0;"></div>
            <div style="font-size:0.72rem;color:rgba(245,166,35,0.8);font-weight:700;
                        letter-spacing:0.16em;text-transform:uppercase;margin-bottom:10px;">
                Utah · The Startup State
            </div>
            <h1 style="color:#fff;margin:0 0 .5rem;font-size:2rem;font-weight:800;letter-spacing:-0.02em;">
                Hey Investor — find the next big thing.
            </h1>
            <p style="color:rgba(255,255,255,.7);margin:0;font-size:1rem;line-height:1.6;">
                Utah is one of the fastest-growing startup ecosystems in the country. Explore the live map,
                filter by stage and industry, and save the companies worth a second look.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tab_c1, tab_c2, _ = st.columns([1, 1, 5])
    if tab_c1.button(
        "🗺️  Map",
        use_container_width=True,
        type="primary" if st.session_state.investor_tab == "map" else "secondary",
        key="itab_map",
    ):
        st.session_state.investor_tab = "map"
        st.rerun()
    if tab_c2.button(
        saved_label,
        use_container_width=True,
        type="primary" if st.session_state.investor_tab == "saved" else "secondary",
        key="itab_saved",
    ):
        st.session_state.investor_tab = "saved"
        st.rerun()
    st.markdown("---")

    if st.session_state.investor_tab == "saved":
        _show_saved_tab(df, user["id"])
        return

    # ── Map tab ───────────────────────────────────────────────────────────────
    # Separate mapped vs unmapped rows
    has_coords = df["lat"].notna() & df["lon"].notna()
    mapped_df   = df[has_coords].copy()
    unmapped_df = df[~has_coords].copy()

    # Read current filter state (before rendering UI so we can filter the map)
    stage_filter, section_filter = _compute_filters(df)

    # Apply filters to mapped rows only (unmapped shown separately)
    plot_df = mapped_df.copy()
    if stage_filter:
        plot_df = plot_df[plot_df["stage"].isin(stage_filter)]
    if section_filter:
        plot_df = plot_df[plot_df["section"].isin(section_filter)]

    # ── Side-by-side: filter panel + map ─────────────────────────────────────
    filter_col, map_col = st.columns([1, 3], gap="medium")

    with filter_col:
        _render_filter_panel(df)

    with map_col:
        n_unmapped = len(unmapped_df)
        n_mapped   = len(mapped_df)
        n_shown    = len(plot_df)

        info_col, recenter_col = st.columns([4, 1])
        if n_unmapped:
            info_col.caption(
                f"{n_shown} of {n_mapped} on map"
                f" · {n_unmapped} without an address — see below"
            )
        else:
            info_col.caption(f"{n_shown} of {n_mapped} startups shown")

        if recenter_col.button("📍 Recenter", use_container_width=True, key="map_recenter"):
            st.session_state.map_render_key = st.session_state.get("map_render_key", 0) + 1
            st.rerun()

        render_key = st.session_state.get("map_render_key", 0)
        clicked_name = _render_map(plot_df, render_key)
        # Only flag a scroll when a genuinely new dot is clicked
        if clicked_name and clicked_name != st.session_state.get("map_selected_name"):
            st.session_state.map_selected_name = clicked_name
            st.session_state.map_scroll_to_card = True
        elif clicked_name:
            st.session_state.map_selected_name = clicked_name

        _render_legend()

    # ── Selection card ────────────────────────────────────────────────────────
    should_scroll = st.session_state.pop("map_scroll_to_card", False)
    selected_name = st.session_state.get("map_selected_name")
    if selected_name:
        st.markdown('<div id="selection-card-anchor"></div>', unsafe_allow_html=True)
        match = df[df["startup_name"] == selected_name]
        if not match.empty:
            _show_selection_card(match.iloc[0], user["id"])
        else:
            st.session_state.pop("map_selected_name", None)

    if should_scroll:
        components.html(
            """<script>
            (function() {
                var el = window.parent.document.getElementById('selection-card-anchor');
                if (el) { el.scrollIntoView({behavior: 'smooth', block: 'center'}); }
            })();
            </script>""",
            height=0,
        )

    # ── Unmapped startups ─────────────────────────────────────────────────────
    if not unmapped_df.empty:
        _show_unmapped(unmapped_df, user["id"])

    # ── Kanban list ───────────────────────────────────────────────────────────
    st.markdown("---")
    _show_list_view(plot_df, user["id"])
