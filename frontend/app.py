import streamlit as st
from utils.styles import apply_styles

st.set_page_config(
    page_title="Alignithm.AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()


def main():
    from utils.auth import is_logged_in, show_auth_page, api

    if not is_logged_in():
        show_auth_page()
        return

    # ── Sidebar ──
    with st.sidebar:
        # Logo / Branding
        st.markdown("""
<div style="text-align:center;padding:0.8rem 0 0.6rem;">
  <div style="font-size:1.5rem;font-weight:800;
              background:linear-gradient(135deg,#E8E8F0 0%,#8B5CF6 50%,#6366F1 100%);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;
              font-family:'Inter',sans-serif;letter-spacing:-0.02em;">
    Alignithm.AI
  </div>
  <div style="display:inline-block;background:rgba(139,92,246,0.15);
              border:1px solid rgba(139,92,246,0.25);border-radius:20px;
              padding:0.15rem 0.7rem;font-size:0.65rem;color:#A78BFA;
              font-weight:600;letter-spacing:0.08em;margin-top:0.3rem;
              font-family:'Inter',sans-serif;text-transform:uppercase;">
    ✨ Career Intelligence
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div style="height:0.3rem;"></div>', unsafe_allow_html=True)

        PAGES = {
            "📊 Dashboard":     "dashboard",
            "📄 Resume":        "resume",
            "💼 Jobs":          "jobs",
            "🎯 Match Report":  "match",
            "✉️ Cover Letter":  "coverletter",
            "📈 Skill Gap":     "skillgap",
            "🗺️ Roadmap":       "roadmap",
            "🎭 Recruiter Sim": "recruiter",
            "🚀 Projects":      "projects",
            "📋 Versions":      "versions",
            "⚙️ Settings":      "profile",
        }

        choice = st.radio(
            "Navigation",
            list(PAGES.keys()),
            label_visibility="collapsed",
            key="nav",
        )
        page_key = PAGES[choice]

        st.markdown("""
<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(139,92,246,0.25),transparent);
            margin:0.8rem 0;"></div>
""", unsafe_allow_html=True)

        # ── AI Provider Toggle ──
        user = st.session_state.get("user", {})
        provider = user.get("ai_provider", "gemini")
        has_key = user.get("has_api_key", False)

        dot_color = "#22c55e" if has_key else "#f59e0b"
        st.markdown(f"""
<div style="background:rgba(19,19,43,0.6);border:1px solid rgba(139,92,246,0.12);
            border-radius:10px;padding:0.6rem 0.8rem;margin:0.3rem 0;">
  <div style="font-size:0.65rem;color:#6B6B8D;text-transform:uppercase;
              letter-spacing:0.08em;font-weight:600;font-family:'Inter',sans-serif;">
    AI Provider
  </div>
  <div style="font-size:0.85rem;font-weight:600;color:#E8E8F0;margin-top:0.15rem;
              font-family:'Inter',sans-serif;">
    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                 background:{dot_color};margin-right:6px;vertical-align:middle;
                 box-shadow:0 0 6px {dot_color}60;"></span>
    {provider.upper()}
  </div>
</div>
""", unsafe_allow_html=True)

        # ── API Key Warning ──
        if not has_key:
            st.markdown("""
<div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
            border-radius:10px;padding:0.6rem 0.8rem;margin-top:0.5rem;">
  <div style="font-size:0.78rem;color:#FCD34D;font-weight:600;
              font-family:'Inter',sans-serif;">
    ⚠️ API key not configured
  </div>
  <div style="font-size:0.7rem;color:#9B9BB0;margin-top:0.2rem;
              font-family:'Inter',sans-serif;">
    Go to Settings to add your key
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(139,92,246,0.25),transparent);
            margin:0.8rem 0;"></div>
""", unsafe_allow_html=True)

        # ── User info / Sign out ──
        email = user.get("email", "")
        if email:
            st.markdown(f"""
<div style="font-size:0.75rem;color:#8B8BA8;font-family:'Inter',sans-serif;
            padding:0 0.2rem;">
  <span style="color:#A78BFA;">●</span> {email}
</div>
""", unsafe_allow_html=True)

        if st.button("Sign Out", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # ── Page Router ──
    from pages_custom import (
        dashboard, resume, jobs, match, coverletter,
        skillgap, roadmap, recruiter, projects, versions, profile,
    )
    router = {
        "dashboard": dashboard, "resume": resume, "jobs": jobs,
        "match": match, "coverletter": coverletter, "skillgap": skillgap,
        "roadmap": roadmap, "recruiter": recruiter, "projects": projects,
        "versions": versions, "profile": profile,
    }
    router[page_key].render()


if __name__ == "__main__":
    main()