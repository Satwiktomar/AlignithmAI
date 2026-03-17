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

    tab_profile, tab_api, tab_danger = st.tabs(["Profile", "API Keys", "Danger Zone"])

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
        st.markdown("#### AI Provider")

        current_provider = user_data.get("ai_provider", "gemini")
        provider = st.radio(
            "Choose your AI provider",
            options=["gemini", "openai"],
            index=0 if current_provider == "gemini" else 1,
            format_func=lambda x: "Google Gemini (free tier available)" if x == "gemini" else "OpenAI (requires paid key)",
            horizontal=True,
            key="provider_radio",
        )

        # Save provider change immediately
        if provider != current_provider:
            r_prov = api("PUT", "/auth/me", json={"ai_provider": provider})
            if r_prov and r_prov.ok:
                st.success(f"Switched to **{provider.upper()}** provider.")
                st.rerun()

        st.divider()

        # ── Gemini key section ──────────────────────────────────────────
        st.markdown("#### Gemini API Key")
        has_gemini = user_data.get("has_api_key", False) if current_provider == "gemini" else bool(user_data.get("has_api_key", False))
        # Recalculate: has_api_key depends on active provider in the model,
        # so check the raw field via a different indicator
        gemini_configured = user_data.get("has_api_key", False) if current_provider == "gemini" else False
        # Use a simple heuristic: if provider is gemini and has_api_key is true
        if current_provider == "gemini" and user_data.get("has_api_key", False):
            st.success("✅ Gemini key is configured and active.")
        elif current_provider != "gemini" and user_data.get("has_api_key", False):
            # Provider is openai but gemini key might still exist
            st.info("Gemini key is saved but **OpenAI** is your active provider.")
        else:
            st.warning("No Gemini API key configured.")

        st.markdown(
            "Get a free key at [aistudio.google.com](https://aistudio.google.com). "
            "Your key is encrypted with AES-256 (Fernet) before storage."
        )
        new_gemini_key = st.text_input(
            "Enter Gemini API Key",
            type="password",
            placeholder="AIza...",
            key="gemini_key_input",
        )
        col_gsave, col_gremove = st.columns(2)
        with col_gsave:
            if st.button("Save Gemini Key", use_container_width=True, disabled=not new_gemini_key):
                r_update = api("PUT", "/auth/me", json={"gemini_api_key": new_gemini_key})
                if r_update and r_update.ok:
                    st.success("Gemini API key saved and encrypted.")
                    st.rerun()
                else:
                    st.error("Failed to save Gemini key.")
        with col_gremove:
            if st.button("Remove Gemini Key", use_container_width=True):
                r_update = api("PUT", "/auth/me", json={"gemini_api_key": ""})
                if r_update and r_update.ok:
                    st.success("Gemini key removed.")
                    st.rerun()
                else:
                    st.error("Failed to remove key.")

        st.divider()

        # ── OpenAI key section ──────────────────────────────────────────
        st.markdown("#### OpenAI API Key")
        has_openai = user_data.get("has_openai_key", False)
        if current_provider == "openai" and has_openai:
            st.success("✅ OpenAI key is configured and active.")
        elif current_provider != "openai" and has_openai:
            st.info("OpenAI key is saved but **Gemini** is your active provider.")
        else:
            st.warning("No OpenAI API key configured.")

        st.markdown(
            "Get a key at [platform.openai.com](https://platform.openai.com/api-keys). "
            "Your key is encrypted with AES-256 (Fernet) before storage."
        )
        new_openai_key = st.text_input(
            "Enter OpenAI API Key",
            type="password",
            placeholder="sk-...",
            key="openai_key_input",
        )
        col_osave, col_oremove = st.columns(2)
        with col_osave:
            if st.button("Save OpenAI Key", use_container_width=True, disabled=not new_openai_key):
                r_update = api("PUT", "/auth/me", json={"openai_api_key": new_openai_key})
                if r_update and r_update.ok:
                    st.success("OpenAI API key saved and encrypted.")
                    st.rerun()
                else:
                    st.error("Failed to save OpenAI key.")
        with col_oremove:
            if has_openai:
                if st.button("Remove OpenAI Key", use_container_width=True):
                    r_update = api("PUT", "/auth/me", json={"openai_api_key": ""})
                    if r_update and r_update.ok:
                        st.success("OpenAI key removed.")
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
