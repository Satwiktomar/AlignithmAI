import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_URL", "http://localhost:8000/api")


def api(method: str, path: str, timeout: int = 30, **kwargs):
    token = st.session_state.get("token")
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        return requests.request(method, f"{API_BASE}{path}", headers=headers, timeout=timeout, **kwargs)
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure the server is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out.")
        return None


def is_logged_in():
    return bool(st.session_state.get("token"))


def show_auth_page():
    # ── Background ──
    st.markdown("""
<style>
.auth-wrapper {
    animation: fadeInUp 0.6s ease;
}
</style>
""", unsafe_allow_html=True)

    _, center, _ = st.columns([1, 2, 1])

    with center:
        # ── Branding ──
        st.markdown("""
<div class="auth-wrapper" style="text-align:center;padding:2.5rem 0 1.5rem;">
  <div style="font-size:2.4rem;font-weight:800;
              background:linear-gradient(135deg,#FFFFFF 0%,#8B5CF6 50%,#6366F1 100%);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;
              font-family:'Inter',sans-serif;letter-spacing:-0.03em;
              margin-bottom:0.3rem;">
    Alignithm.AI
  </div>
  <p style="color:#8B8BA8;font-size:0.95rem;font-family:'Inter',sans-serif;margin:0;">
    Your AI-powered career intelligence platform
  </p>
  <div style="display:inline-block;background:rgba(139,92,246,0.1);
              border:1px solid rgba(139,92,246,0.2);border-radius:20px;
              padding:0.2rem 0.8rem;font-size:0.65rem;color:#A78BFA;
              font-weight:600;letter-spacing:0.08em;margin-top:0.6rem;
              font-family:'Inter',sans-serif;text-transform:uppercase;">
    v1.0 · Resume · Match · Cover Letter · Skill Gap
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Auth Card ──
        st.markdown("""
<div style="background:rgba(19,19,43,0.7);border:1px solid rgba(139,92,246,0.15);
            border-radius:16px;padding:0.6rem;margin:0 auto;max-width:420px;
            backdrop-filter:blur(16px);
            box-shadow:0 8px 40px rgba(10,10,27,0.5);">
""", unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="you@example.com")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        r = api("POST", "/auth/login", json={"email": email, "password": password})
                        if r and r.ok:
                            data = r.json()
                            st.session_state["token"] = data["access_token"]
                            st.session_state["user"] = data.get("user", {})
                            st.rerun()
                        elif r:
                            st.error(r.json().get("detail", "Login failed."))

        with tab_register:
            with st.form("register_form"):
                name = st.text_input("👤 Name", placeholder="Your full name")
                email_r = st.text_input("📧 Email", placeholder="you@example.com", key="reg_email")
                password_r = st.text_input("🔒 Password", type="password", placeholder="Create a password", key="reg_pass")
                submitted_r = st.form_submit_button("Create Account", use_container_width=True)
                if submitted_r:
                    if not name or not email_r or not password_r:
                        st.error("All fields are required.")
                    elif len(password_r) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        r = api("POST", "/auth/register", json={
                            "name": name, "email": email_r, "password": password_r
                        })
                        if r and r.ok:
                            data = r.json()
                            st.session_state["token"] = data["access_token"]
                            st.session_state["user"] = data.get("user", {})
                            st.rerun()
                        elif r:
                            st.error(r.json().get("detail", "Registration failed."))

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Footer ──
        st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0.5rem;">
  <p style="color:#4B4B6B;font-size:0.72rem;font-family:'Inter',sans-serif;">
    AI-powered resume matching · Cover letter generation · Skill gap analysis
  </p>
</div>
""", unsafe_allow_html=True)