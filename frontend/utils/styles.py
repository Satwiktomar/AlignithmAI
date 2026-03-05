def apply_styles():
    import streamlit as st
    st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background-color: #0f1117;
    color: #e0e0e0;
}

.stApp {
    background-color: #0f1117;
}

header, footer, #MainMenu {
    visibility: hidden;
}

section[data-testid="stSidebar"] {
    background-color: #1a1d27 !important;
    border-right: 1px solid #2a2d3a;
}

.stButton > button {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1.2rem;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.15s ease;
}

.stButton > button:hover {
    background-color: #1d4ed8;
}

.stButton > button:disabled {
    background-color: #374151;
    color: #6b7280;
    cursor: not-allowed;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #1a1d27 !important;
    border: 1px solid #2a2d3a !important;
    border-radius: 6px !important;
    color: #e0e0e0 !important;
    font-size: 0.9rem !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.2) !important;
}

.stSelectbox > div > div {
    background-color: #1a1d27 !important;
    border: 1px solid #2a2d3a !important;
    border-radius: 6px !important;
    color: #e0e0e0 !important;
}

div[data-testid="stFileUploader"] {
    border: 1px dashed #2a2d3a !important;
    border-radius: 6px !important;
    background-color: #1a1d27 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #2a2d3a;
    gap: 0;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6b7280;
    font-size: 0.875rem;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border: none;
    border-bottom: 2px solid transparent;
}

.stTabs [aria-selected="true"] {
    color: #e0e0e0 !important;
    border-bottom: 2px solid #2563eb !important;
    background: transparent !important;
    box-shadow: none !important;
}

.stExpander {
    background-color: #1a1d27 !important;
    border: 1px solid #2a2d3a !important;
    border-radius: 6px !important;
}

.stProgress > div > div > div {
    background: #2563eb !important;
    border-radius: 2px !important;
}

.stProgress > div > div {
    background: #2a2d3a !important;
    border-radius: 2px !important;
}

.stAlert {
    border-radius: 6px !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #f0f0f0;
}

hr {
    border-color: #2a2d3a;
}

.stRadio label, .stCheckbox label {
    color: #c0c0c0 !important;
}

p, span, div {
    color: inherit;
}
</style>
""", unsafe_allow_html=True)


def score_color(score: float) -> str:
    if score >= 75:
        return "#22c55e"
    elif score >= 50:
        return "#f59e0b"
    else:
        return "#ef4444"


def render_score_ring(score: float, label: str = "Score"):
    color = score_color(score)
    import streamlit as st
    st.markdown(f"""
<div style="text-align:center; padding:1rem 0;">
  <div style="font-size:2.5rem; font-weight:700; color:{color};">{int(score)}</div>
  <div style="font-size:0.8rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.05em;">{label}</div>
</div>
""", unsafe_allow_html=True)


def render_badge(text: str, badge_type: str = "skill"):
    import streamlit as st
    colors = {
        "skill": ("#1e3a5f", "#93c5fd"),
        "missing": ("#3f1f1f", "#f87171"),
        "matched": ("#1a3a2a", "#4ade80"),
    }
    bg, fg = colors.get(badge_type, ("#1e3a5f", "#93c5fd"))
    st.markdown(
        f'<span style="display:inline-block;padding:0.15rem 0.6rem;border-radius:4px;'
        f'font-size:0.78rem;font-weight:500;background:{bg};color:{fg};margin:2px;">'
        f'{text}</span>',
        unsafe_allow_html=True
    )


def render_stat_card(number, label: str):
    import streamlit as st
    st.markdown(f"""
<div style="border:1px solid #2a2d3a;border-radius:6px;padding:1.2rem;text-align:center;background:#1a1d27;">
  <div style="font-size:2rem;font-weight:700;color:#f0f0f0;">{number}</div>
  <div style="font-size:0.8rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-top:0.2rem;">{label}</div>
</div>
""", unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = ""):
    import streamlit as st
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<p style='color:#6b7280;margin-top:-0.5rem;font-size:0.9rem;'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("---")


def render_empty_state(icon, title: str, body: str):
    import streamlit as st
    st.markdown(f"""
<div style="text-align:center;padding:2rem 1rem;color:#6b7280;">
  <div style="font-size:1rem;font-weight:600;color:#9ca3af;margin-bottom:0.4rem;">{title}</div>
  <div style="font-size:0.875rem;">{body}</div>
</div>
""", unsafe_allow_html=True)
