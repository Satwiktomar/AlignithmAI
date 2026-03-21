def apply_styles():
    import streamlit as st
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background-color: #0A0A1B;
    color: #E8E8F0;
}
.stApp {
    background: #0A0A1B;
}

header, footer, #MainMenu { visibility: hidden; }

/* ── Custom scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0A0A1B; }
::-webkit-scrollbar-thumb { background: #2D2B55; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #8B5CF6; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #13132B 0%, #0E0E22 100%) !important;
    border-right: 1px solid rgba(139,92,246,0.15) !important;
}
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #8B5CF6, #6366F1, #8B5CF6);
    z-index: 999;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7C3AED 0%, #6366F1 100%);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1.4rem;
    font-size: 0.875rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 8px rgba(124,58,237,0.25);
    letter-spacing: 0.01em;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(124,58,237,0.4);
}
.stButton > button:active {
    transform: translateY(0);
}
.stButton > button:disabled {
    background: #1E1E3A;
    color: #4B4B6B;
    cursor: not-allowed;
    box-shadow: none;
}

/* ── Form submit button ── */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #7C3AED 0%, #6366F1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 2px 8px rgba(124,58,237,0.25) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,0.4) !important;
}

/* ── Text inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: rgba(19,19,43,0.8) !important;
    border: 1px solid rgba(139,92,246,0.2) !important;
    border-radius: 10px !important;
    color: #E8E8F0 !important;
    font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
    backdrop-filter: blur(4px) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #8B5CF6 !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.15), 0 0 20px rgba(139,92,246,0.1) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background-color: rgba(19,19,43,0.8) !important;
    border: 1px solid rgba(139,92,246,0.2) !important;
    border-radius: 10px !important;
    color: #E8E8F0 !important;
}

/* ── File uploader ── */
div[data-testid="stFileUploader"] {
    border: 2px dashed rgba(139,92,246,0.3) !important;
    border-radius: 12px !important;
    background: rgba(19,19,43,0.5) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color: rgba(139,92,246,0.6) !important;
    background: rgba(19,19,43,0.7) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid rgba(139,92,246,0.15);
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6B6B8D;
    font-size: 0.875rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    padding: 0.6rem 1.2rem;
    border: none;
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #A5A5C0;
}
.stTabs [aria-selected="true"] {
    color: #E8E8F0 !important;
    border-bottom: 2px solid #8B5CF6 !important;
    background: linear-gradient(180deg, rgba(139,92,246,0.08) 0%, transparent 100%) !important;
    box-shadow: none !important;
}

/* ── Expander ── */
.stExpander {
    background: rgba(19,19,43,0.6) !important;
    border: 1px solid rgba(139,92,246,0.12) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(8px) !important;
    transition: all 0.2s ease !important;
}
.stExpander:hover {
    border-color: rgba(139,92,246,0.25) !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #7C3AED, #6366F1, #8B5CF6) !important;
    border-radius: 4px !important;
}
.stProgress > div > div {
    background: rgba(19,19,43,0.6) !important;
    border-radius: 4px !important;
}

/* ── Alert ── */
.stAlert { border-radius: 12px !important; }

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 {
    color: #F0F0F8;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background: rgba(19,19,43,0.6);
    border: 1px solid rgba(139,92,246,0.12);
    border-radius: 12px;
    padding: 1rem;
    backdrop-filter: blur(8px);
}
div[data-testid="stMetric"] label {
    color: #8B8BA8 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #E8E8F0 !important;
    font-weight: 700 !important;
}

hr {
    border-color: rgba(139,92,246,0.12);
}

/* ── Radio / checkbox ── */
.stRadio label, .stCheckbox label {
    color: #B0B0CC !important;
}

p, span, div { color: inherit; }

/* ── Keyframes ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 8px rgba(139,92,246,0.2); }
    50% { box-shadow: 0 0 20px rgba(139,92,246,0.4); }
}
@keyframes scoreReveal {
    from { stroke-dashoffset: 283; }
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


def render_score_ring(score: float, label: str = "Score", size: int = 120):
    """Animated SVG circular progress ring."""
    color = score_color(score)
    r = 40
    circ = 2 * 3.14159 * r
    offset = circ * (1 - score / 100)
    import streamlit as st
    st.markdown(f"""
<div style="text-align:center;padding:0.8rem 0;animation:fadeInUp 0.5s ease;">
  <svg width="{size}" height="{size}" viewBox="0 0 100 100" style="transform:rotate(-90deg);">
    <circle cx="50" cy="50" r="{r}" fill="none" stroke="rgba(139,92,246,0.1)" stroke-width="8"/>
    <circle cx="50" cy="50" r="{r}" fill="none" stroke="{color}" stroke-width="8"
            stroke-linecap="round"
            stroke-dasharray="{circ}"
            stroke-dashoffset="{offset}"
            style="transition: stroke-dashoffset 1s ease; animation: scoreReveal 1.2s ease forwards;">
      <animate attributeName="stroke-dashoffset" from="{circ}" to="{offset}" dur="1.2s" fill="freeze"/>
    </circle>
  </svg>
  <div style="margin-top:-{size//2 + 16}px; position:relative;">
    <div style="font-size:1.8rem;font-weight:800;color:{color};font-family:'Inter',sans-serif;
                text-shadow:0 0 20px {color}40;">{int(score)}</div>
    <div style="font-size:0.7rem;color:#8B8BA8;text-transform:uppercase;letter-spacing:0.1em;
                font-weight:600;margin-top:2px;">{label}</div>
  </div>
  <div style="height:{size//2 - 10}px;"></div>
</div>
""", unsafe_allow_html=True)


def render_badge(text: str, badge_type: str = "skill"):
    import streamlit as st
    colors = {
        "skill":   ("rgba(99,102,241,0.15)", "#A5B4FC", "rgba(99,102,241,0.3)"),
        "missing": ("rgba(239,68,68,0.12)",  "#FCA5A5", "rgba(239,68,68,0.25)"),
        "matched": ("rgba(34,197,94,0.12)",  "#86EFAC", "rgba(34,197,94,0.25)"),
    }
    bg, fg, border = colors.get(badge_type, colors["skill"])
    st.markdown(
        f'<span style="display:inline-block;padding:0.2rem 0.7rem;border-radius:20px;'
        f'font-size:0.78rem;font-weight:600;background:{bg};color:{fg};'
        f'border:1px solid {border};margin:2px;font-family:\'Inter\',sans-serif;'
        f'transition:transform 0.15s ease;">'
        f'{text}</span>',
        unsafe_allow_html=True
    )


def render_stat_card(number, label: str, icon: str = ""):
    import streamlit as st
    st.markdown(f"""
<div style="background:rgba(19,19,43,0.7);border:1px solid rgba(139,92,246,0.15);
            border-radius:14px;padding:1.3rem 1rem;text-align:center;
            backdrop-filter:blur(12px);transition:all 0.3s ease;
            border-top:2px solid rgba(139,92,246,0.3);
            animation:fadeInUp 0.5s ease;"
     onmouseover="this.style.transform='translateY(-3px)';this.style.boxShadow='0 8px 30px rgba(139,92,246,0.15)'"
     onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
  <div style="font-size:0.7rem;color:#8B8BA8;text-transform:uppercase;letter-spacing:0.1em;
              font-weight:600;margin-bottom:0.4rem;font-family:'Inter',sans-serif;">
    {icon + ' ' if icon else ''}{label}
  </div>
  <div style="font-size:2rem;font-weight:800;color:#F0F0F8;font-family:'Inter',sans-serif;
              line-height:1;">
    {number}
  </div>
</div>
""", unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = ""):
    import streamlit as st
    st.markdown(f"""
<div style="margin-bottom:1.5rem;animation:fadeInUp 0.4s ease;">
  <h2 style="background:linear-gradient(135deg,#E8E8F0 0%,#8B5CF6 100%);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             font-size:1.65rem;font-weight:800;margin-bottom:0.2rem;
             font-family:'Inter',sans-serif;">{title}</h2>
  {f'<p style="color:#8B8BA8;font-size:0.88rem;margin:0;font-family:Inter,sans-serif;">{subtitle}</p>' if subtitle else ''}
</div>
<div style="height:1px;background:linear-gradient(90deg,rgba(139,92,246,0.3),transparent);margin-bottom:1.2rem;"></div>
""", unsafe_allow_html=True)


def render_empty_state(icon, title: str, body: str):
    import streamlit as st
    st.markdown(f"""
<div style="text-align:center;padding:2.5rem 1.5rem;color:#6B6B8D;
            background:rgba(19,19,43,0.4);border-radius:16px;
            border:1px dashed rgba(139,92,246,0.2);margin:1rem 0;
            animation:fadeInUp 0.5s ease;">
  <div style="font-size:1rem;font-weight:700;color:#A5A5C0;margin-bottom:0.5rem;
              font-family:'Inter',sans-serif;">{title}</div>
  <div style="font-size:0.85rem;line-height:1.5;font-family:'Inter',sans-serif;">{body}</div>
</div>
""", unsafe_allow_html=True)


def render_metric_row(metrics: list):
    """Render a horizontal row of metric cards. Each metric is a dict with keys: value, label, icon (optional)."""
    import streamlit as st
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            render_stat_card(m.get("value", 0), m.get("label", ""), m.get("icon", ""))


def render_section_card(content_html: str, accent_color: str = "#8B5CF6"):
    """Glassmorphism content card with accent stripe."""
    import streamlit as st
    st.markdown(f"""
<div style="background:rgba(19,19,43,0.5);border:1px solid rgba(139,92,246,0.12);
            border-radius:14px;padding:1.2rem 1.4rem;margin:0.5rem 0;
            backdrop-filter:blur(12px);border-left:3px solid {accent_color};
            animation:fadeInUp 0.5s ease;">
  {content_html}
</div>
""", unsafe_allow_html=True)
