"""
Investor dashboard — saved startups list.
"""
import streamlit as st
import pandas as pd

from modules.profile_manager import (
    load_saved_startups,
    toggle_saved_startup,
    get_all_public_profiles,
)
from modules.messaging import get_unread_count
from config.settings import STAGE_COLORS, CACHE_DIR, DATA_DIR

import json


def _load_all_startups() -> pd.DataFrame:
    frames = []

    # Primary: processed_data.json — same IDs used when saving from the map
    processed_path = DATA_DIR / "processed_data.json"
    if processed_path.exists():
        with open(processed_path, encoding="utf-8") as f:
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
            })
        if rows:
            frames.append(pd.DataFrame(rows))

    # Fallback: legacy sample_startups.json
    sample_path = CACHE_DIR / "sample_startups.json"
    if sample_path.exists():
        with open(sample_path, encoding="utf-8") as f:
            frames.append(pd.DataFrame(json.load(f)))

    profiles = get_all_public_profiles()
    if profiles:
        pf = pd.DataFrame(profiles)
        pf["id"] = pf.get("user_id", pf.index.astype(str))
        frames.append(pf)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def show_investor_dashboard(user: dict):
    st.markdown("## ⭐ Saved Startups")

    saved_ids = load_saved_startups(user["id"])
    unread = get_unread_count(user["id"])

    if unread:
        st.info(f"💬 You have **{unread}** unread message(s).")

    if not saved_ids:
        st.markdown(
            "<div style='background:#F8F9FA;border-radius:12px;padding:32px;text-align:center;'>"
            "<div style='font-size:3rem;'>⭐</div>"
            "<h3 style='color:#1B3A5C;'>No saved startups yet</h3>"
            "<p style='color:#6C757D;'>Click any startup on the map and hit "
            "'Save Startup' to bookmark it here.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("🗺️ Go to Startup Map", type="primary"):
            st.session_state.current_page = "i_map"
            st.rerun()
        return

    all_startups = _load_all_startups()
    if all_startups.empty:
        st.warning("Could not load startup database.")
        return

    # Filter to saved ones
    saved_df = all_startups[all_startups["id"].astype(str).isin([str(s) for s in saved_ids])]

    st.markdown(f"**{len(saved_df)} saved startups**")
    st.markdown("---")

    for _, row in saved_df.iterrows():
        sid = str(row.get("id", ""))
        stage = str(row.get("stage", ""))
        emp = str(row.get("employees", ""))
        dot_color = STAGE_COLORS.get(stage, "#95A5A6")

        with st.container():
            col_l, col_r = st.columns([3, 1])
            with col_l:
                logo = row.get("logo")
                logo_html = (
                    f"<img src='{logo}' width='48' height='48' "
                    f"style='border-radius:8px;object-fit:cover;margin-right:12px;vertical-align:middle;'>"
                    if logo else ""
                )
                st.markdown(
                    f"""
                    <div style="background:#fff;border-radius:12px;padding:18px 20px;
                                border:1px solid #E9ECEF;box-shadow:0 2px 8px rgba(0,0,0,.04);">
                        <div style="display:flex;align-items:center;margin-bottom:.5rem;">
                            {logo_html}
                            <div>
                                <strong style="color:#1B3A5C;font-size:1.05rem;">
                                    {row.get('startup_name', 'Unknown')}
                                </strong><br>
                                <span style="display:inline-block;width:10px;height:10px;
                                             border-radius:50%;background:{dot_color};
                                             margin-right:5px;"></span>
                                <span style="color:#6C757D;font-size:.85rem;">
                                    {stage} · {emp} employees · {row.get('business_type', '')}
                                </span>
                            </div>
                        </div>
                        <p style="color:#495057;font-size:.9rem;line-height:1.5;margin:0;">
                            {str(row.get('description', ''))[:200]}…
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_r:
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                if row.get("website") and str(row.get("website")) not in ("nan", ""):
                    st.link_button("🌐 Website", str(row["website"]), use_container_width=True)

                if st.button("💬 Message", key=f"msg_{sid}", use_container_width=True):
                    target_user = str(row.get("user_id") or sid)
                    st.session_state.msg_compose_to = target_user
                    st.session_state.msg_compose_name = str(row.get("startup_name", "this founder"))
                    st.session_state.current_page = "i_messages"
                    st.rerun()

                if st.button("💔 Remove", key=f"unsave_{sid}", use_container_width=True):
                    toggle_saved_startup(user["id"], sid)
                    st.rerun()

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
