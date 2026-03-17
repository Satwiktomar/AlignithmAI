import streamlit as st
import requests
import os
import logging

logger = logging.getLogger("rolefit-frontend")

_raw_backend = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
# Ensure the URL has a scheme (https:// or http://)
if _raw_backend and not _raw_backend.startswith(("http://", "https://")):
    _raw_backend = f"https://{_raw_backend}"
API_URL = f"{_raw_backend}/api"

logger.info(f"Frontend API_URL configured as: {API_URL}")


def api(method: str, endpoint: str, **kwargs):
    token = st.session_state.get("token")
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{API_URL}{endpoint}"
    try:
        resp = requests.request(
            method,
            url,
            headers=headers,
            timeout=300,
            **kwargs
        )
        return resp
    except requests.exceptions.ReadTimeout:
        st.error("⏱️ Request timed out — the server is still processing. Try again in a moment.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"🔌 Cannot connect to backend at `{_raw_backend}`. The server may be starting up — please try again in a minute.")
        return None
    except Exception as e:
        st.error(f"Backend not reachable at `{_raw_backend}`: {e}")
        return None


def show_auth_page():
    st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Segoe UI', system-ui, sans-serif; background-color: #0f1117; color: #e0e0e0; }
.stApp { background-color: #0f1117; }
header, footer, #MainMenu { visibility: hidden; }
.stTextInput > div > div > input { background-color: #1a1d27 !important; border: 1px solid #2a2d3a !important; color: #e0e0e0 !important; border-radius: 6px !important; }
.stButton > button { background-color: #2563eb !important; color: #fff !important; border: none !important; border-radius: 6px !important; font-weight: 500 !important; }
h2 { color: #f0f0f0; }
p { color: #9ca3af; }
hr { border-color: #2a2d3a; }
</style>
""", unsafe_allow_html=True)

    st.markdown("## Alignithm.AI")
    st.markdown("AI-powered resume scoring and career tools")
    st.markdown("---")

    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Sign In", use_container_width=True, key="switch_login"):
            st.session_state["auth_mode"] = "login"
            st.rerun()
    with col_b:
        if st.button("Create Account", use_container_width=True, key="switch_register"):
            st.session_state["auth_mode"] = "register"
            st.rerun()

    st.markdown("---")

    if st.session_state["auth_mode"] == "login":
        st.markdown("##### Sign In")
        login_email = st.text_input("Email", key="li_email")
        login_pass = st.text_input("Password", type="password", key="li_pass")
        if st.button("Sign In", use_container_width=True, key="do_login"):
            if not login_email or not login_pass:
                st.error("Enter email and password.")
            else:
                with st.spinner("Signing in..."):
                    r = api("POST", "/auth/login", json={"email": login_email, "password": login_pass})
                if r and r.status_code == 200:
                    data = r.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["user"] = data["user"]
                    st.rerun()
                elif r:
                    try:
                        st.error(r.json().get("detail", "Login failed."))
                    except Exception:
                        st.error(f"Login failed (HTTP {r.status_code}).")

    else:
        st.markdown("##### Create Account")
        reg_name = st.text_input("Full Name", key="re_name")
        reg_email = st.text_input("Email", key="re_email")
        reg_pass = st.text_input("Password", type="password", key="re_pass")
        if st.button("Create Account", use_container_width=True, key="do_register"):
            if not reg_name or not reg_email or not reg_pass:
                st.error("Fill all fields.")
            elif len(reg_pass) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                with st.spinner("Creating account..."):
                    r = api("POST", "/auth/register", json={
                        "name": reg_name,
                        "email": reg_email,
                        "password": reg_pass
                    })
                if r and r.status_code == 200:
                    data = r.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["user"] = data["user"]
                    st.rerun()
                elif r:
                    try:
                        st.error(r.json().get("detail", "Registration failed."))
                    except Exception:
                        st.error(f"Registration failed (HTTP {r.status_code}).")