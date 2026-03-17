import streamlit as st
import os
from utils.styles import apply_styles
from utils.auth import show_auth_page, api

st.set_page_config(
    page_title="Alignithm.AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_styles()

if "token" not in st.session_state:
    pass  # Token stored in session state only (not URL params for security)

if "token" not in st.session_state:
    show_auth_page()
    st.stop()

user = st.session_state.get("user", {})

NAV_ITEMS = {
    "Dashboard": "dashboard",
    "Resume": "resume",
    "Jobs": "jobs",
    "Match": "match",
    "Cover Letter": "coverletter",
    "Skill Gap": "skillgap",
    "Roadmap": "roadmap",
    "Recruiter Sim": "recruiter",
    "Projects": "projects",
    "Versions": "versions",
    "Settings": "profile",
}

if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

with st.sidebar:
    st.markdown(
        "<div style='padding:0.5rem 0 0.25rem;font-size:1.1rem;font-weight:700;color:#f0f0f0;'>Alignithm.AI</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='font-size:0.78rem;color:#6b7280;margin-bottom:0.75rem;'>Career Intelligence Platform</div>",
        unsafe_allow_html=True
    )
    st.markdown("<hr style='border-color:#2a2d3a;margin:0.5rem 0;'>", unsafe_allow_html=True)

    selected = st.radio(
        "Navigation",
        options=list(NAV_ITEMS.keys()),
        index=list(NAV_ITEMS.values()).index(st.session_state["page"]),
        label_visibility="collapsed"
    )

    st.session_state["page"] = NAV_ITEMS[selected]

    st.markdown("<hr style='border-color:#2a2d3a;margin:0.5rem 0;'>", unsafe_allow_html=True)

    # AI Model Toggle
    ollama_status = None
    try:
        import requests as _req
        _backend = os.getenv("BACKEND_URL", "http://localhost:8000")
        _r = api("GET", "/advanced/ollama-status")
        if _r and _r.ok:
            ollama_status = _r.json()
    except Exception:
        pass

    ollama_available = ollama_status.get("available", False) if ollama_status else False
    ollama_ready = ollama_status.get("model_ready", False) if ollama_status else False
    status_dot = "🟢" if ollama_ready else ("🟡" if ollama_available else "🔴")

    current_pref = user.get("prefer_local_model", False)

    use_local = st.toggle(
        f"🖥️ Local AI {status_dot}",
        value=current_pref,
        help="Toggle ON to use local Ollama model. Toggle OFF to use Gemini Cloud AI.",
        key="local_ai_toggle"
    )

    if use_local != current_pref:
        r_toggle = api("PUT", "/auth/me", json={"prefer_local_model": use_local})
        if r_toggle and r_toggle.ok:
            st.session_state["user"]["prefer_local_model"] = use_local
            st.rerun()

    provider_name = user.get("ai_provider", "gemini").upper()
    mode_label = "Local AI (Ollama)" if use_local else f"Cloud AI ({provider_name})"
    st.markdown(
        f"<div style='font-size:0.72rem;color:#6b7280;margin:-0.25rem 0 0.5rem;'>{mode_label}</div>",
        unsafe_allow_html=True
    )

    st.markdown("<hr style='border-color:#2a2d3a;margin:0.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:0.78rem;color:#6b7280;margin-bottom:0.5rem;'>{user.get('email', '')}</div>",
        unsafe_allow_html=True
    )

    if st.button("Sign Out", use_container_width=True):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()

if not user.get("has_api_key", False) and not user.get("prefer_local_model", False):
    provider = user.get("ai_provider", "gemini")
    if provider == "openai":
        st.warning(
            "No OpenAI API key configured — AI features won't work. "
            "Go to **Settings** → **API Keys** to add yours.",
            icon="⚠️"
        )
    else:
        st.warning(
            "No Gemini API key configured — AI features won't work. "
            "Go to **Settings** → **API Keys** to add yours (free at [aistudio.google.com](https://aistudio.google.com)), "
            "or switch to OpenAI in Settings.",
            icon="⚠️"
        )

page = st.session_state["page"]

if page == "dashboard":
    from pages_custom.dashboard import render
    render()
elif page == "resume":
    from pages_custom.resume import render
    render()
elif page == "jobs":
    from pages_custom.jobs import render
    render()
elif page == "match":
    from pages_custom.match import render
    render()
elif page == "coverletter":
    from pages_custom.coverletter import render
    render()
elif page == "skillgap":
    from pages_custom.skillgap import render
    render()
elif page == "roadmap":
    from pages_custom.roadmap import render
    render()
elif page == "recruiter":
    from pages_custom.recruiter import render
    render()
elif page == "projects":
    from pages_custom.projects import render
    render()
elif page == "versions":
    from pages_custom.versions import render
    render()
elif page == "profile":
    from pages_custom.profile import render
    render()