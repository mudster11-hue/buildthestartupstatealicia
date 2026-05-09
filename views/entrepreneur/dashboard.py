import streamlit as st
import streamlit.components.v1 as components
from modules.profile_manager import load_profile, load_saved_grants
from modules.messaging import get_unread_count
from modules.data_loader import load_resources, last_refresh_time


def show_entrepreneur_dashboard(user: dict):
    profile = load_profile(user["id"])
    saved_grants = load_saved_grants(user["id"])
    unread = get_unread_count(user["id"])
    name = profile.get("startup_name") or user["name"]

    # ── Welcome banner ────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #0F2540 0%, #1B3A5C 50%, #1E4A78 100%);
            border-radius: 18px;
            padding: 36px 40px;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(245,166,35,0.18);
            box-shadow: 0 8px 32px rgba(15,37,64,0.18);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position:absolute; top:0; left:0; right:0; height:3px;
                background: linear-gradient(90deg, #F5A623, #FFBC46, transparent);
                border-radius: 18px 18px 0 0;
            "></div>
            <div style="font-size:0.72rem;color:rgba(245,166,35,0.8);font-weight:700;
                        letter-spacing:0.16em;text-transform:uppercase;margin-bottom:10px;">
                Utah · Build the Startup State
            </div>
            <h1 style="color:#fff; margin:0 0 .5rem; font-size:2rem; font-weight:800; letter-spacing:-0.02em;">
                Great ideas make our state the best place to build. Let's get yours going.
            </h1>
            <p style="color:rgba(255,255,255,.7); margin:0; font-size:1rem; line-height:1.6;">
                {'Your startup <strong style="color:rgba(255,255,255,.92);">' + name + '</strong> is on the map.' if profile else "Let’s get your startup profile set up."} &nbsp;Browse 500+ grants, use the grant finder quiz to surface the best matches, and connect directly with Utah investors.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Stat chips ────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    _stat_card(c1, "📋", "Saved Grants", str(len(saved_grants)), "#EBF5FB", "#2980B9",
               scroll_to="saved_grants_anchor" if saved_grants else None)
    _stat_card(c2, "💬", "Unread Messages", str(unread), "#EAFAF1" if unread == 0 else "#FDEDEC",
               "#27AE60" if unread == 0 else "#E74C3C", page_key="e_messages")
    _stat_card(c3, "👤", "Profile",
               "Complete ✓" if _profile_complete(profile) else "Incomplete",
               "#EAFAF1" if _profile_complete(profile) else "#FEF9E7",
               "#27AE60" if _profile_complete(profile) else "#F39C12",
               page_key="e_profile")

    # Scroll to saved grants section if stat card was clicked
    if st.session_state.pop("scroll_to_saved_grants_anchor", False):
        components.html(
            """<script>
            (function() {
                var el = window.parent.document.getElementById('saved-grants-anchor');
                if (el) el.scrollIntoView({behavior: 'smooth', block: 'start'});
            })();
            </script>""",
            height=0,
        )

    st.markdown("---")

    # ── Quick actions ─────────────────────────────────────────────────────────
    st.markdown("### Quick Actions")
    qa1, qa2, qa3 = st.columns(3)

    with qa1:
        st.markdown(
            _action_card("🔍", "Find Grants", "Answer a few questions to get personalized resource matches."),
            unsafe_allow_html=True,
        )
        if st.button("Start Grant Finder", use_container_width=True, type="primary", key="dash_quiz"):
            st.session_state.current_page = "e_quiz"
            st.rerun()

    with qa2:
        st.markdown(
            _action_card("📋", "Browse All Grants", "See every resource in the database — no filtering."),
            unsafe_allow_html=True,
        )
        if st.button("See All Grants", use_container_width=True, key="dash_all"):
            st.session_state.current_page = "e_all_grants"
            st.rerun()

    with qa3:
        label = "Update Profile" if profile else "Build My Profile"
        st.markdown(
            _action_card("👤", label, "Complete your startup profile so investors can find you."),
            unsafe_allow_html=True,
        )
        if st.button(label, use_container_width=True, key="dash_profile"):
            st.session_state.current_page = "e_profile"
            st.rerun()

    # ── Saved grants preview ──────────────────────────────────────────────────
    if saved_grants:
        st.markdown("---")
        st.markdown('<div id="saved-grants-anchor"></div>', unsafe_allow_html=True)
        st.markdown("### ❤️ Your Saved Grants")

        df = load_resources()
        if not df.empty:
            # Try to find title column
            title_col = _find_col(df, ["title", "name", "organization", "resource"])
            if title_col:
                for gid in saved_grants[:5]:
                    row = df[df.index.astype(str) == str(gid)]
                    if not row.empty:
                        r = row.iloc[0]
                        st.markdown(
                            f"<div style='padding:10px 16px; background:#fff; border-radius:10px; "
                            f"border-left:4px solid #F5A623; margin-bottom:8px;'>"
                            f"<strong>{r.get(title_col, 'Resource')}</strong></div>",
                            unsafe_allow_html=True,
                        )
                if len(saved_grants) > 5:
                    st.caption(f"+ {len(saved_grants) - 5} more saved grants")
                if st.button("View All Saved Grants →", key="dash_saved"):
                    st.session_state.current_page = "e_all_grants"
                    st.rerun()

    # ── Last refresh info ─────────────────────────────────────────────────────
    rt = last_refresh_time("resources")
    if rt:
        st.caption(f"Resource data last updated: {rt}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _stat_card(col, icon, label, value, bg, color, page_key=None, scroll_to=None):
    col.markdown(
        f"""
        <div style="background:{bg}; border-radius:12px; padding:20px 16px; text-align:center;">
            <div style="font-size:1.8rem;">{icon}</div>
            <div style="color:{color}; font-size:1.6rem; font-weight:700;">{value}</div>
            <div style="color:#6C757D; font-size:.85rem;">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if page_key:
        if col.button(f"View {label} →", key=f"stat_{page_key}", use_container_width=True):
            st.session_state.current_page = page_key
            st.rerun()
    elif scroll_to:
        if col.button(f"View {label} →", key=f"stat_scroll_{scroll_to}", use_container_width=True):
            st.session_state[f"scroll_to_{scroll_to}"] = True
            st.rerun()


def _action_card(icon, title, desc):
    return (
        f"<div style='background:#fff; border-radius:12px; padding:20px; "
        f"border:1px solid #E9ECEF; min-height:110px; margin-bottom:10px;'>"
        f"<div style='font-size:1.8rem;'>{icon}</div>"
        f"<strong style='color:#1B3A5C;'>{title}</strong>"
        f"<p style='color:#6C757D; font-size:.85rem; margin:.4rem 0 0;'>{desc}</p>"
        f"</div>"
    )


def _find_col(df, candidates):
    for c in df.columns:
        if c.lower().strip() in candidates:
            return c
    return None


def _profile_complete(profile: dict) -> bool:
    required = ["startup_name", "address", "description", "stage"]
    return all(profile.get(f) for f in required)
