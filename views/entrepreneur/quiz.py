import streamlit as st
from modules.data_loader import load_resources
from modules.questionnaire import build_questions
from modules.resource_filter import filter_resources
from config.settings import STAGE_OPTIONS


def show_quiz(user: dict):
    st.markdown("## 🔍 Find Your Resources")
    st.markdown(
        "Answer a few short questions and we'll filter the database down to "
        "the grants and resources that actually apply to your startup.",
    )

    # ── Load & cache data/questions in session ────────────────────────────────
    if "quiz_df" not in st.session_state:
        with st.spinner("Loading resource database…"):
            df = load_resources()
            st.session_state.quiz_df = df

    df = st.session_state.quiz_df

    if df.empty:
        st.warning(
            "Could not reach the resource database right now. "
            "Check your internet connection and try refreshing."
        )
        return

    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = build_questions(df)
        st.session_state.quiz_answers = {}
        st.session_state.quiz_step = 0

    questions = st.session_state.quiz_questions
    answers = st.session_state.quiz_answers
    step = st.session_state.quiz_step
    total = len(questions)

    # ── Results screen ────────────────────────────────────────────────────────
    if step >= total:
        filtered = filter_resources(df, answers)
        st.session_state.quiz_results = filtered

        count = len(filtered)
        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,#1B3A5C,#2E5C8E);
                        border-radius:16px;padding:36px;text-align:center;margin-bottom:1.5rem;">
                <div style="font-size:3rem;">🎉</div>
                <h2 style="color:#fff;margin:.5rem 0;">We found {count} matching resources!</h2>
                <p style="color:rgba(255,255,255,.8);margin:0;">
                    Based on your answers, here are the grants and programs tailored for you.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📋 View My Matches", type="primary", use_container_width=True):
                st.session_state.current_page = "e_quiz_results"
                st.rerun()
        with col_b:
            if st.button("🔄 Start Over", use_container_width=True):
                for k in ["quiz_df", "quiz_questions", "quiz_answers", "quiz_step", "quiz_results"]:
                    st.session_state.pop(k, None)
                st.rerun()
        return

    # ── Progress bar ──────────────────────────────────────────────────────────
    st.progress((step) / total)
    st.caption(f"Question {step + 1} of {total}")

    q = questions[step]
    emoji = q.get("emoji", "❓")
    subtitle = q.get("subtitle", "")

    # Question card
    st.markdown(
        f"""
        <div style="background:#fff;border-radius:16px;padding:40px 36px;
                    border:1px solid #E9ECEF;text-align:center;margin:1rem 0 1.5rem;">
            <div style="font-size:3rem;margin-bottom:.75rem;">{emoji}</div>
            <h2 style="color:#1B3A5C;margin:0 0 .4rem;">{q['question']}</h2>
            {"<p style='color:#6C757D;margin:0;'>" + subtitle + "</p>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Answer widget ─────────────────────────────────────────────────────────
    current = answers.get(q["key"])
    q_type = q.get("type", "single")

    if q_type == "multi":
        default = current if isinstance(current, list) else []
        selected = st.multiselect(
            "Select all that apply:",
            options=q["options"],
            default=default,
            key=f"q_{step}",
        )

    elif q_type == "single_described":
        opts = q["options"]
        descs = q.get("option_descriptions", {})
        labels = [f"{o}  —  {descs.get(o, '')}" for o in opts]
        default_idx = opts.index(current) if current in opts else 0
        chosen_label = st.radio("", labels, index=default_idx, key=f"q_{step}")
        selected = opts[labels.index(chosen_label)]

    else:  # single
        default_idx = q["options"].index(current) if current in q["options"] else 0
        selected = st.radio("", q["options"], index=default_idx, key=f"q_{step}")

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    nav_l, nav_c, nav_r = st.columns([1, 2, 1])

    with nav_l:
        if step > 0:
            if st.button("← Back"):
                st.session_state.quiz_step -= 1
                st.rerun()

    with nav_c:
        if st.button("Skip this question", use_container_width=True):
            st.session_state.quiz_step += 1
            st.rerun()

    with nav_r:
        label = "Next →" if step < total - 1 else "See My Matches 🎉"
        if st.button(label, type="primary"):
            st.session_state.quiz_answers[q["key"]] = selected
            st.session_state.quiz_step += 1
            st.rerun()
