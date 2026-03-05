import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state, score_color


def render():
    render_page_header("Recruiter Simulation", "Get honest AI recruiter feedback on your application")

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

    if st.button("Run Recruiter Simulation", use_container_width=True):
        with st.spinner("Simulating recruiter review..."):
            r = api("POST", "/advanced/recruiter-sim", params={"resume_id": resume_opts[sel_r], "job_id": job_opts[sel_j]})
        if r and r.ok:
            st.session_state["recruiter_result"] = r.json()
        elif r:
            st.error(r.json().get("detail", "Simulation failed."))

    result = st.session_state.get("recruiter_result")
    if not result:
        return

    st.markdown("---")

    verdict = result.get("shortlist_decision", result.get("verdict", ""))
    st.markdown(f"**Verdict:** {verdict}")

    if result.get("first_impression"):
        st.info(result["first_impression"])

    cols = st.columns(3)
    for col, (label, key) in zip(cols, [("Technical Fit", "technical_score"), ("Experience Fit", "experience_score"), ("Culture Fit", "culture_score")]):
        with col:
            st.metric(label, int(float(result.get(key, 0))))

    c1, c2 = st.columns(2)
    with c1:
        if result.get("strengths"):
            with st.expander("Strengths"):
                for s in result["strengths"]:
                    st.markdown(f"- {s}")
    with c2:
        if result.get("red_flags"):
            with st.expander("Red Flags"):
                for f in result["red_flags"]:
                    st.markdown(f"- {f}")

    if result.get("advice"):
        st.markdown("**Advice**")
        advice = result["advice"]
        if isinstance(advice, list):
            for a in advice:
                st.markdown(f"- {a}")
        else:
            st.write(advice)
