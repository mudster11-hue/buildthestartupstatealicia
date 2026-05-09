import streamlit as st
from config.settings import DEMO_USERS


def get_current_user() -> dict | None:
    return st.session_state.get("user", None)


def login_as(role: str):
    user = DEMO_USERS[role].copy()
    st.session_state.user = user
    default_page = "e_dashboard" if role == "entrepreneur" else "i_map"
    st.session_state.current_page = default_page


def clear_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
