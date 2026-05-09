"""
Build the Startup State.
Run with:  streamlit run app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import streamlit.components.v1 as components
from config.settings import APP_ICON, APP_TITLE
from modules.auth import clear_session, get_current_user, login_as

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Global CSS ────────────────────────────────────────────────────────────────

def _apply_styles():
    st.markdown('<a id="page-top"></a>', unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* ── Sidebar ── */
        [data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(180deg, #0F2540 0%, #1B3A5C 55%, #162F4A 100%);
            border-right: 1px solid rgba(245,166,35,0.12);
        }
        [data-testid="stSidebar"] * { color: white !important; }

        /* Gold accent line at the top of the sidebar */
        [data-testid="stSidebar"] > div:first-child > div:first-child::before {
            content: '';
            display: block;
            height: 3px;
            background: linear-gradient(90deg, #F5A623 0%, #FFBC46 50%, transparent 100%);
            margin-bottom: 0;
            border-radius: 0 2px 2px 0;
        }

        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,.07);
            border: 1px solid rgba(255,255,255,.15);
            border-radius: 9px;
            color: white !important;
            margin-bottom: 4px;
            text-align: left;
            transition: background .15s, border-color .15s;
            font-weight: 500;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,.14);
            border-color: rgba(255,255,255,.25);
        }
        /* Active nav button */
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: #F5A623 !important;
            border-color: #F5A623 !important;
            color: #0F2540 !important;
            font-weight: 700;
        }

        /* ── Main content ── */
        .block-container { padding-top: 1.5rem !important; }

        /* Subtle warm background tint on the main area */
        [data-testid="stMain"], .main {
            background: #F8F9FB !important;
        }

        /* Cards */
        .hub-card {
            background: white;
            border-radius: 14px;
            padding: 20px 24px;
            border: 1px solid #EAECEF;
            box-shadow: 0 2px 12px rgba(27,58,92,.06);
            margin-bottom: 12px;
        }

        /* Primary buttons outside sidebar */
        .stButton > button[kind="primary"] {
            background: #F5A623 !important;
            border-color: #F5A623 !important;
            color: #1B3A5C !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            transition: background .15s, box-shadow .15s !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: #F7B540 !important;
            box-shadow: 0 4px 16px rgba(245,166,35,.35) !important;
        }

        /* Secondary buttons outside sidebar */
        .stButton > button[kind="secondary"] {
            border-radius: 10px !important;
            font-weight: 500 !important;
        }

        /* Hide Streamlit branding */
        #MainMenu { visibility: hidden; }
        footer     { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Sidebar navigation ────────────────────────────────────────────────────────

def _render_sidebar(user: dict) -> str:
    with st.sidebar:
        st.markdown(
            "<div style='padding:4px 0 12px;'>"
            "<div style='font-size:1.15rem;font-weight:800;letter-spacing:-0.01em;'>Build the Startup State.</div>"
            "<div style='font-size:0.72rem;color:rgba(255,255,255,0.45)!important;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px;'>Utah · Demo</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(f"**{user['name']}**")
        st.caption(user["role"].title())
        st.markdown("---")

        if user["role"] == "entrepreneur":
            nav = {
                "🏠  Dashboard":      "e_dashboard",
                "🔍  Find Grants":    "e_quiz",
                "📋  All Grants":     "e_all_grants",
                "👤  My Profile":     "e_profile",
                "💬  Messages":       "e_messages",
            }
        else:
            nav = {
                "🗺️  Startup Map": "i_map",
                "💬  Messages":    "i_messages",
            }

        current = st.session_state.get("current_page", list(nav.values())[0])

        for label, page_key in nav.items():
            kind = "primary" if current == page_key else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=kind):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")
        if st.button("↩  Switch Role", use_container_width=True):
            clear_session()
            st.rerun()

    return current


# ── Router ────────────────────────────────────────────────────────────────────

def _route_entrepreneur(page: str, user: dict):
    if page == "e_dashboard":
        from views.entrepreneur.dashboard import show_entrepreneur_dashboard
        show_entrepreneur_dashboard(user)
    elif page == "e_quiz":
        from views.entrepreneur.quiz import show_quiz
        show_quiz(user)
    elif page in ("e_all_grants", "e_quiz_results"):
        from views.entrepreneur.resources import show_resources
        show_resources(user, show_all=(page == "e_all_grants"))
    elif page == "e_profile":
        from views.entrepreneur.profile import show_profile
        show_profile(user)
    elif page == "e_messages":
        from views.entrepreneur.messages import show_messages
        show_messages(user)
    else:
        from views.entrepreneur.dashboard import show_entrepreneur_dashboard
        show_entrepreneur_dashboard(user)


def _route_investor(page: str, user: dict):
    if page in ("i_map", "i_saved"):
        from views.investor.map_view import show_investor_map
        show_investor_map(user)
    elif page == "i_messages":
        from views.investor.messages import show_investor_messages
        show_investor_messages(user)
    else:
        from views.investor.map_view import show_investor_map
        show_investor_map(user)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Handle URL-based role selection set by the landing page iframe
    params = st.query_params
    if "role" in params and st.session_state.get("user") is None:
        role = params.get("role", "")
        if role in ("entrepreneur", "investor"):
            login_as(role)
            st.query_params.clear()
            st.rerun()

    _apply_styles()

    user = get_current_user()
    if user is None:
        from views.landing import show_landing
        show_landing()
        return

    # Set sensible default page on first load
    if "current_page" not in st.session_state:
        st.session_state.current_page = (
            "e_dashboard" if user["role"] == "entrepreneur" else "i_map"
        )

    page = _render_sidebar(user)

    if st.session_state.get("_prev_page") != page:
        st.session_state._prev_page = page
        components.html(
            """<script>
            (function() {
                if (window.parent.history && window.parent.history.scrollRestoration) {
                    window.parent.history.scrollRestoration = 'manual';
                }
                function scrollTop() {
                    var anchor = window.parent.document.getElementById('page-top');
                    if (anchor) {
                        anchor.scrollIntoView({behavior: 'instant', block: 'start'});
                    } else {
                        var targets = [
                            window.parent.document.querySelector('[data-testid="stMain"]'),
                            window.parent.document.querySelector('.main'),
                            window.parent.document.documentElement,
                            window.parent.document.body
                        ];
                        targets.forEach(function(el) { if (el) el.scrollTop = 0; });
                        window.parent.scrollTo(0, 0);
                    }
                }
                scrollTop();
                setTimeout(scrollTop, 50);
                setTimeout(scrollTop, 200);
            })();
            </script>""",
            height=0,
        )

    if user["role"] == "entrepreneur":
        _route_entrepreneur(page, user)
    else:
        _route_investor(page, user)


if __name__ == "__main__":
    main()
