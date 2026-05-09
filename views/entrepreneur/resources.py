"""
Displays resource/grant cards with save toggles.
Called either after the quiz (filtered) or from "See All Grants".
"""
import streamlit as st
import pandas as pd
from modules.data_loader import load_resources
from modules.profile_manager import load_saved_grants, toggle_saved_grant
from modules.resource_filter import filter_resources


# ── Column name detection ─────────────────────────────────────────────────────

def _col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in df.columns:
        if c.lower().strip() in candidates:
            return c
    return None


# ── Main view ─────────────────────────────────────────────────────────────────

def show_resources(user: dict, show_all: bool = False):
    saved = load_saved_grants(user["id"])

    # Decide which dataset to show
    if show_all:
        st.markdown("## 📋 All Grants & Resources")
        st.markdown("Browse every resource in the database.")
        df = load_resources()
    elif "quiz_results" in st.session_state:
        answers = st.session_state.get("quiz_answers", {})
        st.markdown("## 🎯 Your Matched Resources")
        info_parts = []
        if answers.get("industries"):
            info_parts.append(str(answers["industries"]))
        if answers.get("locations"):
            info_parts.append(str(answers["locations"]))
        if info_parts:
            st.markdown(f"Filtered for: **{' · '.join(info_parts)}**")
        df = st.session_state.quiz_results

        col_toggle, _ = st.columns([1, 3])
        with col_toggle:
            if st.button("📋 See All Grants Instead"):
                st.session_state.current_page = "e_all_grants"
                st.rerun()
    else:
        st.info("Complete the Grant Finder quiz first, or browse all grants below.")
        df = load_resources()

    if df.empty:
        st.warning("No resources available right now — check back soon.")
        return

    # Detect key columns
    title_col = _col(df, ["title", "name", "organization", "resource name", "program"])
    desc_col  = _col(df, ["description", "desc", "about", "details", "summary"])
    link_col  = _col(df, ["link", "url", "website", "apply link", "application url"])
    st.markdown(f"**{len(df)} resources found**")
    st.markdown("---")

    # ── Search / filter bar ───────────────────────────────────────────────────
    search = st.text_input("🔎 Search resources", placeholder="Type a keyword…")
    show_saved_only = st.checkbox("❤️ Show saved only")

    filtered_df = df.copy()
    if search:
        mask = filtered_df.apply(
            lambda row: row.astype(str).str.contains(search, case=False, na=False).any(),
            axis=1,
        )
        filtered_df = filtered_df[mask]

    if show_saved_only:
        filtered_df = filtered_df[filtered_df.index.astype(str).isin([str(s) for s in saved])]

    if filtered_df.empty:
        st.info("No resources match your current filter.")
        return

    # ── Cards ─────────────────────────────────────────────────────────────────
    for i, (idx, row) in enumerate(filtered_df.iterrows()):
        grant_id = str(idx)
        is_saved = grant_id in [str(s) for s in saved]

        title = str(row.get(title_col, f"Resource #{i+1}")) if title_col else f"Resource #{i+1}"
        desc  = str(row.get(desc_col, "")) if desc_col else ""
        link  = str(row.get(link_col, "")) if link_col else ""

        # Extra tags from other columns
        tags_html = ""
        for tag_col in ["communities", "industries", "locations", "topics"]:
            tc = _col(df, [tag_col])
            if tc:
                val = str(row.get(tc, "")).strip()
                if val and val.lower() not in ("nan", "n/a", ""):
                    tags_html += (
                        f"<span style='background:#EBF5FB;color:#2980B9;padding:3px 10px;"
                        f"border-radius:20px;font-size:.75rem;margin-right:6px;'>{val[:40]}</span>"
                    )

        heart = "❤️" if is_saved else "🤍"

        with st.container():
            st.markdown(
                f"""
                <div style="background:#fff;border-radius:12px;padding:20px 24px;
                            border:1px solid #E9ECEF;box-shadow:0 2px 8px rgba(0,0,0,.05);
                            margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <strong style="color:#1B3A5C;font-size:1.05rem;">{title}</strong>
                    </div>
                    <p style="color:#495057;font-size:.9rem;line-height:1.55;margin:.5rem 0;">{desc[:300]}{"…" if len(desc)>300 else ""}</p>
                    <div style="margin-top:.75rem;">{tags_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn_col1, btn_col3, _ = st.columns([1, 1, 4])
            with btn_col1:
                if link and link not in ("nan", ""):
                    st.link_button("🔗 Apply / Learn More", link)
            with btn_col3:
                btn_label = f"{heart} {'Saved' if is_saved else 'Save'}"
                if st.button(btn_label, key=f"save_{grant_id}_{i}"):
                    toggle_saved_grant(user["id"], grant_id)
                    st.rerun()
