"""
Entrepreneur profile builder.
Covers: startup info, stage, employees, business type, logo upload, and
the opt-in toggle that puts the startup on the investor map.
"""
import streamlit as st
from modules.profile_manager import load_profile, save_profile, encode_logo
from modules.geocoder import geocode_address
from config.settings import STAGE_OPTIONS, EMPLOYEE_OPTIONS, BUSINESS_TYPES


def show_profile(user: dict):
    st.markdown("## 👤 My Startup Profile")
    st.markdown(
        "Fill in your startup details. Completing your profile lets investors "
        "discover you on the Utah Startup Map."
    )

    profile = load_profile(user["id"])

    with st.form("profile_form"):
        st.markdown("### 🏢 About Your Startup")

        startup_name = st.text_input(
            "Startup Name *",
            value=profile.get("startup_name", ""),
            placeholder="e.g. TechBridge SLC",
        )

        st.markdown("**Full Address** *")
        st.caption(
            "Format: **123 W 4500 S, Sandy, UT 84070** — "
            "this format lets us place you accurately on the map."
        )
        address = st.text_input(
            "Full Address",
            value=profile.get("address", ""),
            placeholder="123 W 4500 S, Sandy, UT 84070",
            label_visibility="collapsed",
        )

        description = st.text_area(
            "Description of Your Startup *",
            value=profile.get("description", ""),
            placeholder="What problem do you solve and for whom? (2-3 sentences)",
            height=120,
        )

        st.markdown("---")
        st.markdown("### 📊 Stage & Scale")

        # Stage — with friendly descriptions
        stage_labels = {k: v["label"] for k, v in STAGE_OPTIONS.items()}
        stage_keys = list(STAGE_OPTIONS.keys())
        current_stage = profile.get("stage", stage_keys[0])
        stage_idx = stage_keys.index(current_stage) if current_stage in stage_keys else 0

        stage_choice = st.radio(
            "What stage is your startup? *",
            options=stage_keys,
            format_func=lambda k: stage_labels[k],
            index=stage_idx,
            horizontal=False,
        )
        st.caption(STAGE_OPTIONS[stage_choice]["description"])

        current_emp = profile.get("employees", EMPLOYEE_OPTIONS[0])
        emp_idx = EMPLOYEE_OPTIONS.index(current_emp) if current_emp in EMPLOYEE_OPTIONS else 0
        employees = st.select_slider(
            "Number of Employees *",
            options=EMPLOYEE_OPTIONS,
            value=EMPLOYEE_OPTIONS[emp_idx],
        )

        # Business type — with friendly descriptions
        bt_keys = list(BUSINESS_TYPES.keys())
        bt_labels = {k: v["label"] for k, v in BUSINESS_TYPES.items()}
        current_bt = profile.get("business_type", "")
        bt_idx = bt_keys.index(current_bt) if current_bt in bt_keys else 0

        business_type = st.selectbox(
            "Business Type",
            options=bt_keys,
            format_func=lambda k: bt_labels[k],
            index=bt_idx,
        )
        if business_type in BUSINESS_TYPES:
            st.caption(BUSINESS_TYPES[business_type]["description"])

        st.markdown("---")
        st.markdown("### 🌐 Optional Details")

        website = st.text_input(
            "Website",
            value=profile.get("website", ""),
            placeholder="https://yoursite.com",
        )

        st.markdown("**Logo** (optional)")
        st.caption("Upload your startup logo — it'll appear on the investor map popup.")
        logo_file = st.file_uploader(
            "Logo Image",
            type=["png", "jpg", "jpeg", "webp"],
            label_visibility="collapsed",
        )

        # Preview existing logo
        existing_logo = profile.get("logo")
        if existing_logo and not logo_file:
            st.image(existing_logo, width=80)
            st.caption("Current logo")

        st.markdown("---")
        st.markdown("### 🗺️ Investor Visibility")
        st.markdown(
            "<div style='background:#EBF5FB;border-radius:10px;padding:14px 18px;margin-bottom:1rem;'>"
            "<strong style='color:#2980B9;'>Open my profile so investors can potentially find me</strong><br>"
            "<span style='color:#5D6D7E;font-size:.9rem;'>Your startup name, description, stage, "
            "and location will appear as a dot on the Utah investor map. "
            "You can turn this off at any time.</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        open_to_investors = st.checkbox(
            "Yes, show my startup on the investor map",
            value=profile.get("open_to_investors", False),
        )

        st.markdown("---")
        submitted = st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True)

    if submitted:
        if not startup_name.strip():
            st.error("Please enter your startup name.")
            return
        if not address.strip():
            st.error("Please enter your full address.")
            return
        if not description.strip():
            st.error("Please add a short description of your startup.")
            return

        logo_data = encode_logo(logo_file) if logo_file else existing_logo

        # Geocode address so it's ready for the map
        with st.spinner("Saving profile and pinning your location on the map…"):
            lat, lon = geocode_address(address) if address else (None, None)

            new_profile = {
                "startup_name": startup_name.strip(),
                "address": address.strip(),
                "description": description.strip(),
                "stage": stage_choice,
                "employees": employees,
                "business_type": business_type,
                "website": website.strip(),
                "logo": logo_data,
                "open_to_investors": open_to_investors,
                "lat": lat,
                "lon": lon,
            }
            save_profile(user["id"], new_profile)

        st.success("✅ Profile saved! Your changes are live.")

        if open_to_investors and lat:
            st.info("📍 Your startup has been pinned on the investor map.")
        elif open_to_investors and not lat:
            st.warning(
                "We couldn't geocode your address automatically. "
                "Double-check the format and save again to get pinned on the map."
            )

        st.balloons()
