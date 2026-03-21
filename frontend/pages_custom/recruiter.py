import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state, score_color


def render():
    render_page_header("Recruiter Simulator", "See how a recruiter would evaluate your resume")

    r_res = api("GET", "/resume/")
    r_jobs = api("GET", "/jobs/")
    if not r_res or not r_jobs:
        return

    resumes = r_res.json() if r_res.ok else []
    jobs = r_jobs.json() if r_jobs.ok else []

    if not resumes:
        render_empty_state(None, "No resumes", "Upload a resume first.")
        return
    if not jobs:
        render_empty_state(None, "No jobs", "Add a job description first.")
        return

    c1, c2 = st.columns(2)
    with c1:
        resume_opts = {f"{r.get('original_filename', 'Resume')} (#{r['id']})": r["id"] for r in resumes}
        sel_r = st.selectbox("Resume", list(resume_opts.keys()), key="rec_resume")
    with c2:
        job_opts = {f"{j.get('job_title', 'Job')} @ {j.get('company_name', '?')} (#{j['id']})": j["id"] for j in jobs}
        sel_j = st.selectbox("Job", list(job_opts.keys()), key="rec_job")

    if st.button("🎭 Simulate Recruiter Review", use_container_width=True):
        with st.spinner("Simulating recruiter review..."):
            r = api("POST", "/advanced/recruiter-sim", timeout=600,
                    params={"resume_id": resume_opts[sel_r], "job_id": job_opts[sel_j]})
        if r and r.ok:
            st.session_state["recruiter_result"] = r.json()
        elif r:
            detail = ""
            try:
                detail = r.json().get("detail", "")
            except Exception:
                detail = f"HTTP {r.status_code}"
            if r.status_code in (429, 503) or "quota" in detail.lower() or "api key" in detail.lower():
                st.error("🔑 **API Key Issue** — Check your API key in Settings.")
            else:
                st.error(detail or "Simulation failed.")

    result = st.session_state.get("recruiter_result")
    if not result:
        return

    st.markdown("---")

    # ── Verdict Banner ──
    verdict = (result.get("verdict") or "").lower()
    verdict_config = {
        "shortlisted":  ("#22c55e", "rgba(34,197,94,0.08)",  "✅ SHORTLISTED"),
        "shortlist":    ("#22c55e", "rgba(34,197,94,0.08)",  "✅ SHORTLISTED"),
        "rejected":     ("#ef4444", "rgba(239,68,68,0.08)",  "❌ REJECTED"),
        "reject":       ("#ef4444", "rgba(239,68,68,0.08)",  "❌ REJECTED"),
        "maybe":        ("#f59e0b", "rgba(245,158,11,0.08)", "🤔 MAYBE"),
    }
    vcolor, vbg, vlabel = verdict_config.get(verdict, ("#f59e0b", "rgba(245,158,11,0.08)", f"📋 {result.get('verdict', 'Review')}"))

    st.markdown(f"""
<div style="background:{vbg};border:1px solid {vcolor}40;border-radius:14px;
            padding:1.2rem 1.5rem;text-align:center;margin-bottom:1rem;
            animation:fadeInUp 0.5s ease;">
  <div style="font-size:1.3rem;font-weight:800;color:{vcolor};font-family:'Inter',sans-serif;
              letter-spacing:0.05em;">
    {vlabel}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── First Impression ──
    first_imp = result.get("first_impression", "")
    if first_imp:
        st.markdown(f"""
<div style="background:rgba(19,19,43,0.5);border-left:3px solid #8B5CF6;
            border-radius:0 10px 10px 0;padding:0.8rem 1.2rem;margin-bottom:1rem;
            font-style:italic;color:#B0B0CC;font-size:0.88rem;line-height:1.6;
            font-family:'Inter',sans-serif;">
  "{first_imp}"
</div>
""", unsafe_allow_html=True)

    # ── Score Gauges ──
    scores_data = result.get("scores") or {}
    if scores_data:
        score_items = list(scores_data.items())[:6]
        cols = st.columns(min(len(score_items), 4))
        for idx, (key, val) in enumerate(score_items):
            with cols[idx % len(cols)]:
                v = float(val) if val else 0
                color = score_color(v)
                label = key.replace("_", " ").title()
                st.markdown(f"""
<div style="text-align:center;background:rgba(19,19,43,0.5);border:1px solid rgba(139,92,246,0.1);
            border-radius:10px;padding:0.7rem 0.4rem;margin-bottom:0.5rem;
            backdrop-filter:blur(6px);">
  <div style="font-size:0.6rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.06em;
              font-weight:600;font-family:'Inter',sans-serif;">{label}</div>
  <div style="font-size:1.3rem;font-weight:800;color:{color};margin-top:0.15rem;
              font-family:'Inter',sans-serif;">{int(v)}</div>
</div>
""", unsafe_allow_html=True)

    # ── Strengths & Red Flags ──
    col_s, col_r = st.columns(2)
    with col_s:
        strengths = result.get("strengths") or []
        if strengths:
            st.markdown("""
<div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
            font-weight:600;margin-bottom:0.4rem;font-family:'Inter',sans-serif;">💪 Strengths</div>
""", unsafe_allow_html=True)
            for s in strengths:
                text = s.get("point", s) if isinstance(s, dict) else s
                st.markdown(f"""
<div style="background:rgba(34,197,94,0.05);border-left:3px solid #22c55e;
            border-radius:0 8px 8px 0;padding:0.5rem 0.8rem;margin-bottom:0.3rem;
            font-size:0.82rem;color:#B0B0CC;font-family:'Inter',sans-serif;">
  {text}
</div>
""", unsafe_allow_html=True)

    with col_r:
        red_flags = result.get("red_flags") or result.get("weaknesses") or []
        if red_flags:
            st.markdown("""
<div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
            font-weight:600;margin-bottom:0.4rem;font-family:'Inter',sans-serif;">🚩 Red Flags</div>
""", unsafe_allow_html=True)
            for rf in red_flags:
                text = rf.get("point", rf) if isinstance(rf, dict) else rf
                st.markdown(f"""
<div style="background:rgba(239,68,68,0.05);border-left:3px solid #ef4444;
            border-radius:0 8px 8px 0;padding:0.5rem 0.8rem;margin-bottom:0.3rem;
            font-size:0.82rem;color:#B0B0CC;font-family:'Inter',sans-serif;">
  {text}
</div>
""", unsafe_allow_html=True)

    # ── Interview Questions ──
    questions = result.get("interview_questions") or result.get("likely_questions") or []
    if questions:
        st.markdown("---")
        st.markdown("""
<div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
            font-weight:600;margin-bottom:0.5rem;font-family:'Inter',sans-serif;">
  🎤 Likely Interview Questions
</div>
""", unsafe_allow_html=True)
        for q in questions:
            text = q.get("question", q) if isinstance(q, dict) else q
            st.markdown(f"""
<div style="background:rgba(99,102,241,0.05);border-left:3px solid #6366F1;
            border-radius:0 8px 8px 0;padding:0.5rem 0.8rem;margin-bottom:0.3rem;
            font-size:0.82rem;color:#B0B0CC;font-family:'Inter',sans-serif;">
  {text}
</div>
""", unsafe_allow_html=True)

    # ── Tips ──
    tips = result.get("tips") or result.get("improvement_tips") or []
    if tips:
        st.markdown("---")
        st.markdown("#### 💡 Improvement Tips")
        for tip in tips:
            st.markdown(f"- {tip}")
