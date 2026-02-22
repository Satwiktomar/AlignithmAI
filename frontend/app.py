import streamlit as st
from utils.styles import apply_styles
from utils.auth import show_auth_page, api

st.set_page_config(
    page_title="Alignithm.AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_styles()

if "token" not in st.session_state:
    show_auth_page()
    st.stop()

user = st.session_state.get("user", {})

NAV_ITEMS = [
    ("Dashboard", "dashboard"),
    ("Resume", "resume"),
    ("Jobs", "jobs"),
    ("Match", "match"),
    ("Cover Letter", "coverletter"),
    ("Skill Gap", "skillgap"),
    ("Recruiter Sim", "recruiter"),
    ("Projects", "projects"),
    ("Versions", "versions"),
]

if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

with st.sidebar:
    st.markdown(f"""
<div style="padding: 1.2rem 0.5rem 1.5rem; border-bottom: 1px solid #1e293b; margin-bottom: 0.8rem;">
  <div style="font-size:1.2rem; font-weight:800; font-family:'Fira Code', monospace; background:linear-gradient(135deg,#3B82F6,#2563EB);
              -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
    ⚡ Alignithm.AI
  </div>
  <div style="font-size:0.75rem; color:#64748b; margin-top:0.2rem; font-family:'Fira Sans', sans-serif;">Career Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

    for label, key in NAV_ITEMS:
        is_active = st.session_state["page"] == key
        btn_style = "background: rgba(59, 130, 246, 0.15) !important; color:#f8fafc !important;" if is_active else ""
        if st.button(f"{label}", key=f"nav_{key}", use_container_width=True):
            st.session_state["page"] = key
            st.rerun()

    st.markdown("<div style='height:1px; background:#1e293b; margin:1rem 0;'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.78rem; color:#64748b; padding:0 0.5rem;'>👤 {user.get('name','User')}</div>", unsafe_allow_html=True)
    if st.button("Sign Out", key="logout_btn", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

page = st.session_state.get("page", "dashboard")

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
elif page == "recruiter":
    from pages_custom.recruiter import render
    render()
elif page == "projects":
    from pages_custom.projects import render
    render()
elif page == "versions":
    from pages_custom.versions import render
    render()
