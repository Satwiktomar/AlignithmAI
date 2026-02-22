import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state, score_color


def render():
    render_page_header("Recruiter Simulation", "Get brutally honest AI recruiter feedback on your application")

    r_res = api("GET", "/resume/")
    r_jobs = api("GET", "/jobs/")
    if not r_res or not r_jobs:
        return

    resumes = r_res.json() if r_res.ok else []
    jobs = r_jobs.json() if r_jobs.ok else []

    if not resumes:
        render_empty_state("📄", "No resumes", "Upload a resume first.")
        return
    if not jobs:
        render_empty_state("💼", "No jobs", "Add a job description first.")
        return

    c1, c2 = st.columns(2)
    with c1:
        resume_opts = {f"{r.get('original_filename','Resume')} (#{r['id']})": r["id"] for r in resumes}
        sel_r = st.selectbox("Resume", list(resume_opts.keys()))
    with c2:
        job_opts = {f"{j.get('job_title','Job')} @ {j.get('company_name','?')} (#{j['id']})": j["id"] for j in jobs}
        sel_j = st.selectbox("Job", list(job_opts.keys()))

    if st.button("🤖 Run Recruiter Simulation", use_container_width=True):
        with st.spinner("Simulating recruiter review…"):
            r = api("POST", "/advanced/recruiter-sim", params={"resume_id": resume_opts[sel_r], "job_id": job_opts[sel_j]})
        if r and r.ok:
            st.session_state["recruiter_result"] = r.json()
        elif r:
            st.error(r.json().get("detail", "Simulation failed."))

    result = st.session_state.get("recruiter_result")
    if not result:
        return

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    verdict = result.get("shortlist_decision", result.get("verdict", ""))
    shortlisted = "shortlist" in str(verdict).lower() and "not" not in str(verdict).lower()
    verdict_color = "#4ade80" if shortlisted else "#f87171"
    verdict_icon = "✅" if shortlisted else "❌"
    st.markdown(f"""
<div class="info-card" style="border-color:{verdict_color}40; text-align:center; margin-bottom:1.2rem;">
  <div style="font-size:1.8rem">{verdict_icon}</div>
  <div style="font-size:1rem; font-weight:700; color:{verdict_color}; margin-top:0.4rem">{verdict}</div>
</div>
""", unsafe_allow_html=True)

    if result.get("first_impression"):
        st.markdown("**First Impression**")
        st.info(result["first_impression"])

    cols = st.columns(3)
    score_fields = [
        ("Technical Fit", "technical_score"),
        ("Experience Fit", "experience_score"),
        ("Culture Fit", "culture_score")
    ]
    for col, (label, key) in zip(cols, score_fields):
        val = float(result.get(key, 0))
        color = score_color(val)
        with col:
            st.markdown(f"""
<div class="stat-card">
  <div class="stat-number" style="-webkit-text-fill-color:{color}">{int(val)}</div>
  <div class="stat-label">{label}</div>
</div>
""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if result.get("strengths"):
            with st.expander("✅ Strengths"):
                for s in result["strengths"]:
                    st.markdown(f"• {s}")
    with c2:
        if result.get("red_flags"):
            with st.expander("⚠️ Red Flags"):
                for f in result["red_flags"]:
                    st.markdown(f"• {f}")

    if result.get("advice"):
        st.markdown("**Recruiter Advice**")
        advice = result["advice"]
        if isinstance(advice, list):
            for a in advice:
                st.markdown(f"→ {a}")
        else:
            st.write(advice)
