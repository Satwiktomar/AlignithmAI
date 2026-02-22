def apply_styles():
    import streamlit as st
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0d0f14;
    color: #e8eaf0;
}

section[data-testid="stSidebar"] {
    background: #13161e !important;
    border-right: 1px solid #1e2130;
}

section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: none;
    color: #9aa3b8;
    text-align: left;
    width: 100%;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    font-size: 0.88rem;
    font-weight: 500;
    transition: all 0.2s ease;
    margin: 1px 0;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99, 102, 241, 0.12);
    color: #c4c9dc;
}

.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1.4rem;
    font-size: 0.875rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 12px rgba(99, 102, 241, 0.3);
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.45);
    background: linear-gradient(135deg, #7173f5, #9b6cf9);
}

.stButton > button:active {
    transform: translateY(0);
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background: #1a1d2e !important;
    border: 1px solid #252840 !important;
    border-radius: 8px !important;
    color: #e8eaf0 !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
}

.stSelectbox > div > div {
    background: #1a1d2e !important;
    border: 1px solid #252840 !important;
    border-radius: 8px !important;
}

div[data-testid="stFileUploader"] {
    border: 1.5px dashed #2e3352 !important;
    border-radius: 12px !important;
    background: #14172a !important;
    transition: border-color 0.2s;
}

div[data-testid="stFileUploader"]:hover {
    border-color: #6366f1 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #13161e;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
    border-bottom: none;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6b7280;
    border-radius: 7px;
    font-size: 0.86rem;
    font-weight: 500;
    padding: 0.45rem 1.1rem;
    border: none;
    transition: all 0.2s;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
}

.stExpander {
    background: #13161e !important;
    border: 1px solid #1e2130 !important;
    border-radius: 10px !important;
}

.stat-card {
    background: #13161e;
    border: 1px solid #1e2130;
    border-radius: 14px;
    padding: 1.4rem;
    text-align: center;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: 14px 14px 0 0;
}

.stat-card:hover {
    border-color: #2e3352;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}

.stat-number {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}

.stat-label {
    font-size: 0.8rem;
    color: #6b7280;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.page-header {
    margin-bottom: 1.8rem;
}

.page-header h1 {
    font-size: 1.7rem;
    font-weight: 700;
    color: #f1f3f9;
    margin: 0 0 0.3rem 0;
}

.page-header p {
    color: #6b7280;
    font-size: 0.9rem;
    margin: 0;
}

.score-ring-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem 0;
}

.score-ring {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 6px solid;
    position: relative;
}

.score-ring-value {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
}

.score-ring-label {
    font-size: 0.65rem;
    color: #9aa3b8;
    font-weight: 500;
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.info-card {
    background: #13161e;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
}

.badge {
    display: inline-block;
    padding: 0.22rem 0.7rem;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 600;
    margin: 2px;
}

.badge-skill {
    background: rgba(99, 102, 241, 0.15);
    color: #a78bfa;
    border: 1px solid rgba(99, 102, 241, 0.25);
}

.badge-missing {
    background: rgba(239, 68, 68, 0.12);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.2);
}

.badge-matched {
    background: rgba(34, 197, 94, 0.12);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.2);
}

.divider {
    height: 1px;
    background: #1e2130;
    margin: 1.2rem 0;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
    border-radius: 6px !important;
}

.stProgress > div > div {
    background: #1e2130 !important;
    border-radius: 6px !important;
}

.upload-hint {
    font-size: 0.8rem;
    color: #6b7280;
    text-align: center;
    margin-top: 0.4rem;
}

.match-row {
    background: #13161e;
    border: 1px solid #1e2130;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    transition: border-color 0.2s;
}

.match-row:hover {
    border-color: #2e3352;
}

.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #6b7280;
}

.empty-state-icon {
    font-size: 2.5rem;
    margin-bottom: 0.8rem;
    opacity: 0.5;
}

.empty-state h3 {
    color: #9aa3b8;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

.empty-state p {
    font-size: 0.87rem;
}
</style>
""", unsafe_allow_html=True)


def score_color(score: float) -> str:
    if score >= 75:
        return "#4ade80"
    elif score >= 50:
        return "#facc15"
    else:
        return "#f87171"


def render_score_ring(score: float, label: str = "Score"):
    color = score_color(score)
    import streamlit as st
    st.markdown(f"""
<div class="score-ring-container">
  <div class="score-ring" style="border-color: {color}; background: rgba(0,0,0,0.2);">
    <span class="score-ring-value" style="color: {color}">{int(score)}</span>
    <span class="score-ring-label">{label}</span>
  </div>
</div>
""", unsafe_allow_html=True)


def render_badge(text: str, badge_type: str = "skill"):
    import streamlit as st
    st.markdown(f'<span class="badge badge-{badge_type}">{text}</span>', unsafe_allow_html=True)


def render_stat_card(number, label: str):
    import streamlit as st
    st.markdown(f"""
<div class="stat-card">
  <div class="stat-number">{number}</div>
  <div class="stat-label">{label}</div>
</div>
""", unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = ""):
    import streamlit as st
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
<div class="page-header">
  <h1>{title}</h1>
  {sub_html}
</div>
""", unsafe_allow_html=True)


def render_empty_state(icon: str, title: str, body: str):
    import streamlit as st
    st.markdown(f"""
<div class="empty-state">
  <div class="empty-state-icon">{icon}</div>
  <h3>{title}</h3>
  <p>{body}</p>
</div>
""", unsafe_allow_html=True)
