"""Streamlit UI for login, signup, and user settings."""

import base64
from typing import Any, Optional

import streamlit as st

from auth import authenticate_user, get_user_profile, register_user, update_profile


def is_logged_in() -> bool:
    """Return True if a user is logged in."""
    return bool(st.session_state.get("logged_in"))


def set_user_session(user: dict[str, Any]) -> None:
    """
    Store authenticated user data in session state.

    Args:
        user: User dictionary from the database.
    """
    st.session_state.logged_in = True
    st.session_state.user_id = user["id"]
    st.session_state.user_email = user["email"]
    st.session_state.user_name = user["full_name"]
    st.session_state.user_phone = user.get("phone", "")
    st.session_state.user_photo = user.get("profile_photo", "")


def clear_user_session() -> None:
    """Clear authentication and profile data from session state."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.session_state.user_phone = ""
    st.session_state.user_photo = ""
    st.session_state.show_settings = False
    st.session_state.screening_result = None


def init_auth_session_state() -> None:
    """Initialize authentication-related session state keys."""
    defaults = {
        "logged_in": False,
        "user_id": None,
        "user_email": "",
        "user_name": "",
        "user_phone": "",
        "user_photo": "",
        "show_settings": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_auth_page() -> None:
    """Render login and signup forms for unauthenticated users."""
    st.title("AI-Powered Applicant Tracking System")
    st.markdown("Sign in to access the recruiter dashboard.")

    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        st.subheader("Login")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary", key="login_button"):
            success, message, user = authenticate_user(login_email, login_password)
            if success and user:
                set_user_session(user)
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with signup_tab:
        st.subheader("Create Account")
        signup_name = st.text_input("Full Name", key="signup_name")
        signup_email = st.text_input("Email Address", key="signup_email")
        signup_phone = st.text_input("Phone Number (optional)", key="signup_phone")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Create Account", type="primary", key="signup_button"):
            if signup_password != signup_confirm:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(
                    signup_name, signup_email, signup_password, signup_phone
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)


def render_sidebar_user_panel() -> None:
    """Render user info and settings button in the sidebar."""
    with st.sidebar:
        st.markdown("### Account")

        if st.session_state.user_photo:
            try:
                photo_bytes = base64.b64decode(st.session_state.user_photo)
                st.image(photo_bytes, width=80)
            except Exception:
                st.markdown("👤")

        st.markdown(f"**{st.session_state.user_name}**")
        st.caption(st.session_state.user_email)
        if st.session_state.user_phone:
            st.caption(f"📞 {st.session_state.user_phone}")

        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.show_settings = True
            st.rerun()


def render_settings_page() -> None:
    """Render profile settings with photo upload and logout."""
    st.title("Account Settings")

    user = get_user_profile(st.session_state.user_id)
    if not user:
        st.error("Unable to load profile. Please log in again.")
        clear_user_session()
        st.rerun()
        return

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Profile Photo")
        if user.get("profile_photo"):
            try:
                st.image(base64.b64decode(user["profile_photo"]), width=160)
            except Exception:
                st.info("No valid profile photo.")
        else:
            st.info("No profile photo uploaded.")

        uploaded_photo = st.file_uploader(
            "Upload profile photo",
            type=["png", "jpg", "jpeg", "webp"],
            key="profile_photo_upload",
        )

    with col2:
        st.subheader("Personal Information")
        settings_name = st.text_input("Full Name", value=user.get("full_name", ""), key="settings_name")
        settings_email = st.text_input(
            "Email",
            value=user.get("email", ""),
            disabled=True,
            key="settings_email",
        )
        settings_phone = st.text_input(
            "Phone Number",
            value=user.get("phone", ""),
            key="settings_phone",
        )

        photo_data: Optional[str] = None
        if uploaded_photo is not None:
            photo_data = base64.b64encode(uploaded_photo.read()).decode("utf-8")

        if st.button("Save Changes", type="primary"):
            success, message = update_profile(
                user_id=st.session_state.user_id,
                full_name=settings_name,
                phone=settings_phone,
                profile_photo=photo_data,
            )
            if success:
                refreshed = get_user_profile(st.session_state.user_id)
                if refreshed:
                    set_user_session(refreshed)
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    st.divider()

    col_back, col_logout = st.columns(2)
    with col_back:
        if st.button("← Back to Dashboard"):
            st.session_state.show_settings = False
            st.rerun()
    with col_logout:
        if st.button("Logout", type="secondary"):
            clear_user_session()
            st.success("Logged out successfully.")
            st.rerun()
