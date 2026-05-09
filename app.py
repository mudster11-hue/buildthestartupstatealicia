"""
Build the Startup State.
Run with:  streamlit run app.py
"""
import sys
from pathlib import Path

# Make sure the project root is importable
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import streamlit.components.v1 as components
from config.settings import APP_ICON, APP_TITLE
from modules.auth import clear_session, get_current_user

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
        /* Sidebar dark navy */
        [data-testid="stSidebar"] > div:first-child {
            background: #1B3A5C;
        }
        [data-testid="stSidebar"] * { color: white !important; }
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,.08);
            border: 1px solid rgba(255,255,255,.2);
            border-radius: 8px;
            color: white !important;
            margin-bottom: 4px;
            text-align: left;
            transition: background .15s;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,.18);
        }
        /* Active nav button */
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: #F5A623 !important;
            border-color: #F5A623 !important;
            color: #1B3A5C !important;
            font-weight: 700;
        }
        /* Remove default top padding */
        .block-container { padding-top: 1.5rem !important; }
        /* Card helper class */
        .hub-card {
            background: white;
            border-radius: 12px;
            padding: 20px 24px;
            border: 1px solid #E9ECEF;
            box-shadow: 0 2px 8px rgba(0,0,0,.05);
            margin-bottom: 12px;
        }
        /* Hide Streamlit branding */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Sidebar navigation ────────────────────────────────────────────────────────

def _render_sidebar(user: dict) -> str:
    with st.sidebar:
        st.markdown("### 🚀 Build the Startup State.")
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
