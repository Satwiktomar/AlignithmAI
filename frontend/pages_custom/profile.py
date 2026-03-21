import streamlit as st
from utils.auth import api
from utils.styles import render_page_header


def render():
    render_page_header("Settings", "Manage your profile, API keys, and preferences")

    tab_profile, tab_api, tab_danger = st.tabs(["👤 Profile", "🔑 API Keys", "⚠️ Account"])

    user = st.session_state.get("user", {})

    with tab_profile:
        st.markdown(f"""
<div style="background:rgba(19,19,43,0.6);border:1px solid rgba(139,92,246,0.12);
            border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:1rem;
            backdrop-filter:blur(10px);display:flex;align-items:center;gap:1rem;
            animation:fadeInUp 0.4s ease;">
  <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#7C3AED,#6366F1);
              display:flex;align-items:center;justify-content:center;font-size:1.3rem;
              flex-shrink:0;color:white;font-weight:700;font-family:'Inter',sans-serif;">
    {(user.get('name', user.get('email', 'U'))[0:1]).upper()}
  </div>
  <div>
    <div style="font-size:1rem;font-weight:700;color:#E8E8F0;font-family:'Inter',sans-serif;">
      {user.get('name', '—')}
    </div>
    <div style="font-size:0.8rem;color:#8B8BA8;font-family:'Inter',sans-serif;">
      {user.get('email', '—')}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        provider = user.get("ai_provider", "gemini")
        st.markdown(f"""
<div style="background:rgba(19,19,43,0.4);border:1px solid rgba(139,92,246,0.1);
            border-radius:10px;padding:0.7rem 1rem;">
  <div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
              font-weight:600;font-family:'Inter',sans-serif;">Current AI Provider</div>
  <div style="font-size:0.9rem;font-weight:600;color:#E8E8F0;margin-top:0.15rem;
              font-family:'Inter',sans-serif;">{provider.upper()}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div style="height:0.6rem;"></div>', unsafe_allow_html=True)

        new_provider = st.radio("Switch AI Provider", ["gemini", "openai"], horizontal=True,
                                index=0 if provider == "gemini" else 1, key="prov_switch")
        if new_provider != provider:
            if st.button("Update Provider", use_container_width=True):
                r = api("PUT", "/auth/me", json={"ai_provider": new_provider})
                if r and r.ok:
                    st.session_state["user"]["ai_provider"] = new_provider
                    st.success(f"✅ Switched to {new_provider.upper()}")
                    st.rerun()

    with tab_api:
        has_key = user.get("has_api_key", False)
        provider = user.get("ai_provider", "gemini")

        # ── Status ──
        if has_key:
            status_color = "#22c55e"
            status_bg = "rgba(34,197,94,0.08)"
            status_text = "✅ API key configured"
        else:
            status_color = "#f59e0b"
            status_bg = "rgba(245,158,11,0.08)"
            status_text = "⚠️ No API key set"

        st.markdown(f"""
<div style="background:{status_bg};border:1px solid {status_color}30;border-radius:10px;
            padding:0.7rem 1rem;margin-bottom:1rem;">
  <div style="font-size:0.85rem;font-weight:600;color:{status_color};
              font-family:'Inter',sans-serif;">{status_text}</div>
  <div style="font-size:0.75rem;color:#8B8BA8;margin-top:0.1rem;
              font-family:'Inter',sans-serif;">
    Provider: <strong>{provider.upper()}</strong>
  </div>
</div>
""", unsafe_allow_html=True)

        api_key_label = "Gemini API Key" if provider == "gemini" else "OpenAI API Key"
        api_key = st.text_input(api_key_label, type="password",
                                placeholder=f"Enter your {provider.title()} API key")

        if st.button("💾 Save API Key", use_container_width=True):
            if not api_key.strip():
                st.error("Please enter an API key.")
            else:
                key_field = "gemini_api_key" if provider == "gemini" else "openai_api_key"
                r = api("PUT", "/auth/me", json={key_field: api_key.strip()})
                if r and r.ok:
                    st.session_state["user"]["has_api_key"] = True
                    st.success("✅ API key saved!")
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Failed to save key."))

        st.markdown("""
<div style="background:rgba(19,19,43,0.3);border-radius:10px;padding:0.6rem 0.8rem;
            margin-top:0.8rem;">
  <div style="font-size:0.75rem;color:#6B6B8D;line-height:1.5;font-family:'Inter',sans-serif;">
    🔒 Your API key is encrypted and stored securely.
    Get a Gemini key at <a href="https://aistudio.google.com/apikey" target="_blank"
    style="color:#A78BFA;">Google AI Studio</a> or an OpenAI key at
    <a href="https://platform.openai.com/api-keys" target="_blank" style="color:#A78BFA;">OpenAI</a>.
  </div>
</div>
""", unsafe_allow_html=True)

    with tab_danger:
        st.markdown(f"""
<div style="background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.2);
            border-radius:14px;padding:1.2rem 1.4rem;margin-top:0.5rem;">
  <div style="font-size:0.85rem;font-weight:700;color:#FCA5A5;margin-bottom:0.3rem;
              font-family:'Inter',sans-serif;">⚠️ Danger Zone</div>
  <div style="font-size:0.8rem;color:#9B9BB0;font-family:'Inter',sans-serif;
              line-height:1.5;margin-bottom:0.8rem;">
    These actions are irreversible. Deleting your account removes all data permanently.
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

        confirm = st.text_input("Type 'DELETE' to confirm", key="confirm_delete",
                                placeholder="DELETE")
        if st.button("🗑 Delete My Account", use_container_width=True):
            if confirm != "DELETE":
                st.error("Type DELETE to confirm.")
            else:
                r = api("DELETE", "/auth/me")
                if r and r.ok:
                    for k in list(st.session_state.keys()):
                        del st.session_state[k]
                    st.success("Account deleted.")
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Delete failed."))
