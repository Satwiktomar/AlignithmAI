import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state, render_score_ring, score_color


def render():
    render_page_header("Match Report", "AI-powered resume-to-job fit analysis")

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
        sel_r = st.selectbox("Resume", list(resume_opts.keys()))
    with c2:
        job_opts = {f"{j.get('job_title', 'Job')} @ {j.get('company_name', '?')} (#{j['id']})": j["id"] for j in jobs}
        sel_j = st.selectbox("Job", list(job_opts.keys()))

    if st.button("🎯 Analyze Match", use_container_width=True):
        with st.spinner("Running AI match analysis..."):
            r = api("POST", "/match/", timeout=600, json={
                "resume_id": resume_opts[sel_r],
                "job_id": job_opts[sel_j]
            })
        if r and r.ok:
            st.session_state["match_result"] = r.json()
        elif r:
            st.error(r.json().get("detail", "Match failed."))

    result = st.session_state.get("match_result")
    if not result:
        return

    st.markdown("---")

    # ── Overall Score Ring ──
    overall = float(result.get("overall_score", result.get("score", 0)))
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        render_score_ring(overall, "Overall Match", size=140)

    # ── Sub-Scores ──
    sub_keys = [
        ("skill_match_score", "Skill Match", "🛠"),
        ("keyword_score", "Keywords", "🔑"),
        ("experience_score", "Experience", "📊"),
        ("ats_score", "ATS Score", "🤖"),
    ]
    score_cols = st.columns(len(sub_keys))
    for col, (key, label, icon) in zip(score_cols, sub_keys):
        with col:
            val = float(result.get(key, 0))
            color = score_color(val)
            st.markdown(f"""
<div style="text-align:center;background:rgba(19,19,43,0.5);border:1px solid rgba(139,92,246,0.1);
            border-radius:12px;padding:0.8rem 0.5rem;backdrop-filter:blur(6px);
            animation:fadeInUp 0.5s ease;">
  <div style="font-size:0.65rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
              font-weight:600;font-family:'Inter',sans-serif;">{icon} {label}</div>
  <div style="font-size:1.5rem;font-weight:800;color:{color};margin-top:0.2rem;
              font-family:'Inter',sans-serif;">{int(val)}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)

    # ── Skills Breakdown ──
    col_matched, col_missing = st.columns(2)
    with col_matched:
        matched = result.get("matched_skills") or []
        if matched:
            st.markdown("""
<div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
            font-weight:600;margin-bottom:0.4rem;font-family:'Inter',sans-serif;">✅ Matched Skills</div>
""", unsafe_allow_html=True)
            badges = ""
            for sk in matched:
                badges += (
                    f'<span style="display:inline-block;padding:0.2rem 0.65rem;border-radius:16px;'
                    f'font-size:0.73rem;font-weight:600;background:rgba(34,197,94,0.1);'
                    f'color:#86EFAC;border:1px solid rgba(34,197,94,0.25);margin:2px;'
                    f'font-family:\'Inter\',sans-serif;">{sk}</span>'
                )
            st.markdown(badges, unsafe_allow_html=True)

    with col_missing:
        missing = result.get("missing_skills") or []
        if missing:
            st.markdown("""
<div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
            font-weight:600;margin-bottom:0.4rem;font-family:'Inter',sans-serif;">❌ Missing Skills</div>
""", unsafe_allow_html=True)
            badges = ""
            for sk in missing:
                badges += (
                    f'<span style="display:inline-block;padding:0.2rem 0.65rem;border-radius:16px;'
                    f'font-size:0.73rem;font-weight:600;background:rgba(239,68,68,0.1);'
                    f'color:#FCA5A5;border:1px solid rgba(239,68,68,0.25);margin:2px;'
                    f'font-family:\'Inter\',sans-serif;">{sk}</span>'
                )
            st.markdown(badges, unsafe_allow_html=True)

    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

    # ── Analysis Sections ──
    tab_str, tab_weak, tab_sug = st.tabs(["💪 Strengths", "⚠️ Weaknesses", "💡 Suggestions"])

    with tab_str:
        for item in (result.get("strengths") or []):
            st.markdown(f"""
<div style="background:rgba(34,197,94,0.05);border-left:3px solid #22c55e;
            border-radius:0 8px 8px 0;padding:0.6rem 1rem;margin-bottom:0.4rem;
            font-size:0.85rem;color:#B0B0CC;font-family:'Inter',sans-serif;">
  {item}
</div>
""", unsafe_allow_html=True)

    with tab_weak:
        for item in (result.get("weaknesses") or []):
            st.markdown(f"""
<div style="background:rgba(245,158,11,0.05);border-left:3px solid #f59e0b;
            border-radius:0 8px 8px 0;padding:0.6rem 1rem;margin-bottom:0.4rem;
            font-size:0.85rem;color:#B0B0CC;font-family:'Inter',sans-serif;">
  {item}
</div>
""", unsafe_allow_html=True)

    with tab_sug:
        for item in (result.get("suggestions") or []):
            st.markdown(f"""
<div style="background:rgba(99,102,241,0.05);border-left:3px solid #6366F1;
            border-radius:0 8px 8px 0;padding:0.6rem 1rem;margin-bottom:0.4rem;
            font-size:0.85rem;color:#B0B0CC;font-family:'Inter',sans-serif;">
  {item}
</div>
""", unsafe_allow_html=True)
