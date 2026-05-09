"""
Entrepreneur messaging view.
Entrepreneurs receive messages from investors and can reply.
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


def show_messages(user: dict):
    st.markdown("## 💬 Messages")

    threads = get_all_conversations(user["id"])

    if not threads:
        st.info(
            "No messages yet. Once an investor reaches out, their messages will appear here."
        )
        return

    # ── Thread list / conversation selector ───────────────────────────────────
    selected_other = st.session_state.get("msg_open_thread")

    # Sidebar-style thread list
    st.markdown("### Conversations")
    for t in threads:
        other_id = t["other_id"]
        unread = t["unread_count"]
        last_ts = _fmt_time(t["last_timestamp"])
        badge = f" 🔴 {unread}" if unread else ""

        # Try to get a friendly name for the investor
        other_profile = load_profile(other_id)
        other_name = other_profile.get("startup_name") or other_id.replace("_", " ").title()

        label = f"**{other_name}**{badge} — {t['last_message'][:40]}… ({last_ts})"
        if st.button(label, key=f"thread_{other_id}", use_container_width=True):
            st.session_state.msg_open_thread = other_id
            mark_read(user["id"], other_id)
            st.rerun()

    # ── Open thread ───────────────────────────────────────────────────────────
    if selected_other:
        st.markdown("---")
        other_profile = load_profile(selected_other)
        other_name = other_profile.get("startup_name") or selected_other.replace("_", " ").title()
        st.markdown(f"### Conversation with {other_name}")

        msgs = get_conversation(user["id"], selected_other)
        _render_messages(msgs, user["id"])

        with st.form(f"reply_form_{selected_other}", clear_on_submit=True):
            reply = st.text_area("Your reply", placeholder="Type your message…", height=80)
            if st.form_submit_button("Send →", type="primary"):
                if reply.strip():
                    send_message(user["id"], selected_other, reply.strip())
                    st.rerun()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _render_messages(messages: list, current_user_id: str):
    for m in messages:
        is_me = m["sender_id"] == current_user_id
        align = "right" if is_me else "left"
        bg = "#1B3A5C" if is_me else "#F1F3F4"
        color = "#fff" if is_me else "#1B3A5C"
        ts = _fmt_time(m["timestamp"])
        st.markdown(
            f"""
            <div style="display:flex; justify-content:{'flex-end' if is_me else 'flex-start'};
                        margin-bottom:10px;">
                <div style="background:{bg}; color:{color}; border-radius:14px;
                            padding:10px 16px; max-width:70%; font-size:.9rem; line-height:1.5;">
                    {m['text']}
                    <div style="font-size:.7rem; opacity:.6; margin-top:4px; text-align:right;">{ts}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _fmt_time(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%b %d, %I:%M %p")
    except Exception:
        return iso
