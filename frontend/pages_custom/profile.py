import streamlit as st
from utils.auth import api
from utils.styles import render_page_header


def render():
    render_page_header("Settings", "Manage your account, API keys, and preferences")

    r = api("GET", "/auth/me")
    if not r or not r.ok:
        st.error("Error fetching profile.")
        return
    user_data = r.json()

    tab_profile, tab_api, tab_danger = st.tabs(["Profile", "API Key", "Danger Zone"])

    with tab_profile:
        st.markdown(f"**Name:** {user_data.get('name', '')}")
        st.markdown(f"**Email:** {user_data.get('email', '')}")

        with st.expander("Edit Name"):
            new_name = st.text_input("New Name", value=user_data.get("name", ""))
            if st.button("Update Name"):
                r_update = api("PUT", "/auth/me", json={"name": new_name})
                if r_update and r_update.ok:
                    st.success("Name updated.")
                    st.session_state["user"]["name"] = new_name
                    st.rerun()
                else:
                    st.error("Failed to update name.")

    with tab_api:
        st.markdown("#### Gemini API Key")

        has_key = user_data.get("has_api_key", False)
        if has_key:
            st.success("An API key is configured. All AI features are active.")
        else:
            st.warning(
                "No API key configured. AI features (resume parsing, match scoring, "
                "cover letters, skill gap, recruiter sim) will not work until you add a key."
            )

        st.markdown(
            "Get a free key at [aistudio.google.com](https://aistudio.google.com). "
            "Your key is encrypted with AES-256 (Fernet) before being stored. "
            "It is never logged or returned in any API response."
        )

        new_key = st.text_input(
            "Enter Gemini API Key",
            type="password",
            placeholder="Enter your API Key",
            label_visibility="visible"
        )

        col_save, col_remove = st.columns(2)
        with col_save:
            if st.button("Save Key", use_container_width=True, disabled=not new_key):
                r_update = api("PUT", "/auth/me", json={"gemini_api_key": new_key})
                if r_update and r_update.ok:
                    st.success("API key saved and encrypted.")
                    st.rerun()
                else:
                    st.error("Failed to save API key.")
        with col_remove:
            if has_key:
                if st.button("Remove Key", use_container_width=True):
                    r_update = api("PUT", "/auth/me", json={"gemini_api_key": ""})
                    if r_update and r_update.ok:
                        st.success("API key removed.")
                        st.rerun()
                    else:
                        st.error("Failed to remove key.")

    with tab_danger:
        st.markdown("#### Delete Account")
        st.warning("This is permanent. All resumes, jobs, scores, and cover letters will be deleted.")

        validation = st.text_input("Type DELETE to confirm")
        if st.button("Delete My Account"):
            if validation == "DELETE":
                r_del = api("DELETE", "/auth/me")
                if r_del and r_del.ok:
                    for k in list(st.session_state.keys()):
                        del st.session_state[k]
                    st.rerun()
                else:
                    st.error("Error deleting account.")
            else:
                st.error("You must type DELETE to confirm.")
