import streamlit as st
from modules.auth import login_as


def show_landing():
    # Hide sidebar on the landing page
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none}</style>",
        unsafe_allow_html=True,
    )

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #1B3A5C 0%, #2E5C8E 100%);
            padding: 72px 32px 64px;
            text-align: center;
            border-radius: 0 0 24px 24px;
            margin: -4rem -4rem 0 -4rem;
        ">
            <div style="font-size:3.6rem; margin-bottom:.5rem;">🚀</div>
            <h1 style="color:#FFFFFF; font-size:3rem; font-weight:800; margin:0 0 .75rem;">
                Build the Startup State.
            </h1>
            <p style="color:rgba(255,255,255,.82); font-size:1.25rem; max-width:520px;
                      margin:0 auto; line-height:1.6;">
                Utah's platform for founders seeking funding and investors
                discovering the next great company.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Subtle feature strip ───────────────────────────────────────────────────
    st.markdown(
        "<p style='text-align:center;color:#ADB5BD;font-size:.82rem;"
        "margin:1.2rem 0 2rem;letter-spacing:.02em;'>"
        "📋 500+ grants &amp; resources &nbsp;·&nbsp; "
        "🗺️ Live startup map &nbsp;·&nbsp; "
        "🔍 Grant finder quiz"
        "</p>",
        unsafe_allow_html=True,
    )

    # ── Role selector ─────────────────────────────────────────────────────────
    st.markdown('<div id="role-section"></div>', unsafe_allow_html=True)
    st.markdown(
        "<h2 style='text-align:center;color:#1B3A5C;margin-bottom:.25rem;'>Who are you?</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;color:#6C757D;margin-bottom:2rem;font-size:1.05rem;'>"
        "Choose your role to get started — no account needed for the demo.</p>",
        unsafe_allow_html=True,
    )

    col1, spacer, col2 = st.columns([1, 0.08, 1])

    # ── Entrepreneur card ─────────────────────────────────────────────────────
    with col1:
        st.markdown(
            """
            <div style="background:#fff; border-radius:16px; padding:40px 32px;
                        text-align:center; border:2px solid #E9ECEF;
                        box-shadow:0 4px 24px rgba(0,0,0,.07); min-height:280px;">
                <div style="font-size:3.5rem; margin-bottom:.75rem;">💼</div>
                <h2 style="color:#1B3A5C; margin-bottom:.5rem;">I'm an Entrepreneur</h2>
                <p style="color:#6C757D; margin-bottom:1.5rem; line-height:1.6;">
                    Find grants and resources tailored to your startup, build your
                    profile, and connect with investors in Utah.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("Enter as Entrepreneur →", use_container_width=True, type="primary", key="btn_ent"):
            login_as("entrepreneur")
            st.rerun()

    with spacer:
        pass

    # ── Investor card ─────────────────────────────────────────────────────────
    with col2:
        st.markdown(
            """
            <div style="background:#fff; border-radius:16px; padding:40px 32px;
                        text-align:center; border:2px solid #E9ECEF;
                        box-shadow:0 4px 24px rgba(0,0,0,.07); min-height:280px;">
                <div style="font-size:3.5rem; margin-bottom:.75rem;">📊</div>
                <h2 style="color:#1B3A5C; margin-bottom:.5rem;">I'm an Investor</h2>
                <p style="color:#6C757D; margin-bottom:1.5rem; line-height:1.6;">
                    Explore Utah's startup ecosystem on an interactive map,
                    save promising companies, and discover Utah founders.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("Enter as Investor →", use_container_width=True, key="btn_inv"):
            login_as("investor")
            st.rerun()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#ADB5BD;font-size:.8rem;'>"
        "Build the Startup State. · Demo Mode · Data refreshes every 60 minutes</p>",
        unsafe_allow_html=True,
    )
