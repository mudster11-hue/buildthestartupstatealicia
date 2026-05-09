"""
Investor messaging view.
Investors initiate conversations with entrepreneurs and manage replies.
"""
import streamlit as st
from datetime import datetime

from modules.messaging import (
    get_all_conversations,
    get_conversation,
    send_message,
    mark_read,
)
from modules.profile_manager import load_profile


def show_investor_messages(user: dict):
    st.markdown("## 💬 Messages")

    # Pre-fill compose if triggered from map "Message Founder" button
    compose_to   = st.session_state.pop("msg_compose_to", None)
    compose_name = st.session_state.pop("msg_compose_name", None)

    if compose_to:
        st.session_state.inv_msg_open = compose_to
        st.session_state.inv_msg_open_name = compose_name

    # ── New message composer ──────────────────────────────────────────────────
    with st.expander("✏️ Start a new conversation", expanded=bool(st.session_state.get("inv_msg_open"))):
        prefill_id   = st.session_state.get("inv_msg_open", "")
        prefill_name = st.session_state.get("inv_msg_open_name", "")

        if prefill_name:
            # Triggered from map — show name, not the raw internal ID
            st.markdown(
                f"<div style='background:#EBF5FB;border-radius:8px;padding:10px 14px;"
                f"margin-bottom:10px;font-size:.9rem;'>"
                f"<span style='color:#6C757D;'>To:</span> "
                f"<strong style='color:#1B3A5C;'>{prefill_name}</strong>"
                f"</div>",
                unsafe_allow_html=True,
            )
            recipient_id = prefill_id
        else:
            recipient_id = st.text_input(
                "Startup or Entrepreneur ID",
                value=prefill_id,
                placeholder="e.g. demo_entrepreneur",
                help="Enter the user ID of the entrepreneur you'd like to contact.",
            )

        with st.form("new_msg_form", clear_on_submit=True):
            msg_text = st.text_area(
                "Message",
                placeholder="Introduce yourself and explain your interest…",
                height=120,
            )
            if st.form_submit_button("Send Message →", type="primary"):
                if recipient_id.strip() and msg_text.strip():
                    send_message(user["id"], recipient_id.strip(), msg_text.strip())
                    st.session_state.inv_active_thread = recipient_id.strip()
                    st.session_state.pop("inv_msg_open", None)
                    st.session_state.pop("inv_msg_open_name", None)
                    st.success("Message sent!")
                    st.rerun()
                else:
                    st.error("Please enter a message.")

    # ── Existing threads ──────────────────────────────────────────────────────
    threads = get_all_conversations(user["id"])

    if not threads:
        st.info("No conversations yet. Use the form above to reach out to a founder.")
        return

    st.markdown("### Your Conversations")
    active = st.session_state.get("inv_active_thread")

    for t in threads:
        other_id = t["other_id"]
        unread   = t["unread_count"]
        last_ts  = _fmt_time(t["last_timestamp"])
        badge    = f" 🔴 {unread}" if unread else ""

        other_profile = load_profile(other_id)
        other_name = (
            other_profile.get("startup_name")
            or other_id.replace("_", " ").title()
        )

        label = f"**{other_name}**{badge}  —  {t['last_message'][:40]}… ({last_ts})"
        if st.button(label, key=f"inv_thread_{other_id}", use_container_width=True):
            st.session_state.inv_active_thread = other_id
            mark_read(user["id"], other_id)
            st.rerun()

    # ── Open thread ───────────────────────────────────────────────────────────
    if active:
        st.markdown("---")
        other_profile = load_profile(active)
        other_name = other_profile.get("startup_name") or active.replace("_", " ").title()
        st.markdown(f"### {other_name}")

        msgs = get_conversation(user["id"], active)
        for m in msgs:
            is_me = m["sender_id"] == user["id"]
            bg    = "#1B3A5C" if is_me else "#F1F3F4"
            color = "#fff" if is_me else "#1B3A5C"
            ts    = _fmt_time(m["timestamp"])
            st.markdown(
                f"""
                <div style="display:flex;justify-content:{'flex-end' if is_me else 'flex-start'};
                            margin-bottom:10px;">
                    <div style="background:{bg};color:{color};border-radius:14px;
                                padding:10px 16px;max-width:70%;font-size:.9rem;line-height:1.5;">
                        {m['text']}
                        <div style="font-size:.7rem;opacity:.6;margin-top:4px;text-align:right;">{ts}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.form(f"inv_reply_{active}", clear_on_submit=True):
            reply = st.text_area("Reply", placeholder="Continue the conversation…", height=80)
            if st.form_submit_button("Send →", type="primary"):
                if reply.strip():
                    send_message(user["id"], active, reply.strip())
                    st.rerun()


def _fmt_time(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%b %d, %I:%M %p")
    except Exception:
        return iso
