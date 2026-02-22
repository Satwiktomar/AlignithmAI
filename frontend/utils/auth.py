import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/api")


def api(method: str, endpoint: str, **kwargs):
    token = st.session_state.get("token")
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.request(method, f"{API_URL}{endpoint}", headers=headers, **kwargs)
        return resp
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend — make sure the API server is running on port 8000.")
        return None


def show_auth_page():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

section[data-testid="stSidebar"] { display: none; }
header[data-testid="stHeader"] { display: none; }
#MainMenu { display: none; }
footer { display: none; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

.auth-root {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #0d0f14;
    background-image:
        radial-gradient(ellipse 60% 40% at 20% 10%, rgba(99,102,241,0.15) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 80% 90%, rgba(167,139,250,0.10) 0%, transparent 60%);
    padding: 2rem 1rem;
}

.auth-panel {
    width: 100%;
    max-width: 440px;
    margin: 0 auto;
}

.auth-logo-wrap {
    text-align: center;
    margin-bottom: 2rem;
}

.brand-icon {
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, #6366f1, #a78bfa);
    border-radius: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 8px 32px rgba(99,102,241,0.35);
}

.brand-name {
    font-size: 1.75rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6366f1 0%, #a78bfa 50%, #c4b5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1;
}

.brand-tagline {
    font-size: 0.85rem;
    color: #6b7280;
    margin-top: 0.4rem;
    font-weight: 400;
}

.auth-card {
    background: #13161e;
    border: 1px solid #1e2130;
    border-radius: 20px;
    padding: 2.2rem 2rem 2rem;
    box-shadow: 0 24px 64px rgba(0,0,0,0.4);
}

.feature-grid {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 1.8rem;
}

.feature-pill {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.18);
    color: #9aa3b8;
    font-size: 0.73rem;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-weight: 500;
}

/* Override Streamlit tab styles */
.stTabs [data-baseweb="tab-list"] {
    background: #0d0f14 !important;
    border-radius: 10px !important;
    padding: 3px !important;
    gap: 2px !important;
    border: 1px solid #1e2130;
    margin-bottom: 1.4rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    color: #6b7280 !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.45rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #7c3aed) !important;
    color: #fff !important;
}

/* Input overrides */
.stTextInput input {
    background: #0d0f14 !important;
    border: 1px solid #2a2d3e !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
    padding: 0.65rem 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
.stTextInput label { color: #9aa3b8 !important; font-size: 0.82rem !important; font-weight: 500 !important; }

/* Primary button */
.stButton > button[kind="primary"], .stButton > button {
    background: linear-gradient(135deg, #6366f1, #7c3aed) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.2rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s !important;
    cursor: pointer !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
</style>
""", unsafe_allow_html=True)

    st.markdown('<div class="auth-root"><div class="auth-panel">', unsafe_allow_html=True)

    st.markdown("""
<div class="auth-logo-wrap">
  <div class="brand-icon">⚡</div>
  <div class="brand-name">Alignithm.AI</div>
  <div class="brand-tagline">AI-powered resume &amp; career intelligence</div>
</div>
<div class="auth-card">
""", unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        email = st.text_input("Email address", key="login_email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign In →", use_container_width=True, key="login_btn"):
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                r = api("POST", "/auth/login", json={"email": email, "password": password})
                if r and r.status_code == 200:
                    data = r.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["user"] = data["user"]
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Login failed."))

    with tab_register:
        name = st.text_input("Full name", key="reg_name", placeholder="Jane Smith")
        email_r = st.text_input("Email address", key="reg_email", placeholder="you@example.com")
        password_r = st.text_input("Password", type="password", key="reg_password", placeholder="Min. 8 characters")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Create Account →", use_container_width=True, key="register_btn"):
            if not name or not email_r or not password_r:
                st.error("Please fill in all fields.")
            elif len(password_r) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                r = api("POST", "/auth/register", json={"name": name, "email": email_r, "password": password_r})
                if r and r.status_code == 200:
                    data = r.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["user"] = data["user"]
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Registration failed."))

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
<div class="feature-grid">
  <span class="feature-pill">📄 Smart Resume Parsing</span>
  <span class="feature-pill">🎯 Match Scoring</span>
  <span class="feature-pill">✍️ Cover Letter AI</span>
  <span class="feature-pill">📊 Skill Gap Analysis</span>
  <span class="feature-pill">🤖 Recruiter Simulation</span>
  <span class="feature-pill">🗂️ Project Ranker</span>
</div>
</div></div>
""", unsafe_allow_html=True)
