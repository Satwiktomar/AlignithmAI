import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state, score_color


def render():
    render_page_header("Match Report", "Score your resume against a job description")

    r_resumes = api("GET", "/resume/")
    r_jobs = api("GET", "/jobs/")

    if not r_resumes or not r_jobs:
        return

    resumes = r_resumes.json() if r_resumes.ok else []
    jobs = r_jobs.json() if r_jobs.ok else []

    if not resumes:
        render_empty_state(None, "No resumes uploaded", "Upload a resume first from the Resume page.")
        return
    if not jobs:
        render_empty_state(None, "No jobs added", "Analyze a job description first from the Jobs page.")
        return

    col1, col2 = st.columns(2)
    with col1:
        resume_options = {f"{r.get('original_filename', 'Resume')} (#{r['id']})": r["id"] for r in resumes}
        sel_resume_label = st.selectbox("Resume", list(resume_options.keys()))
        resume_id = resume_options[sel_resume_label]
    with col2:
        job_options = {f"{j.get('job_title','') or 'Job'} @ {j.get('company_name','') or '?'} (#{j['id']})": j["id"] for j in jobs}
        sel_job_label = st.selectbox("Job Description", list(job_options.keys()))
        job_id = job_options[sel_job_label]

    if st.button("Run Match Analysis", use_container_width=True):
        with st.spinner("Analyzing..."):
            r = api("POST", "/match/", params={"resume_id": resume_id, "job_id": job_id})
        if not r or not r.ok:
            st.error(r.json().get("detail", "Match analysis failed.") if r else "API error.")
            return
        st.session_state["last_match"] = r.json()

    ms = st.session_state.get("last_match")
    if not ms:
        return

    st.markdown("---")

    overall = float(ms.get("overall_score", 0))
    st.markdown(f"### Overall Score: {int(overall)}")

    sub_scores = [
        ("Skill Match", "skill_score"),
        ("Keyword", "keyword_score"),
        ("Experience", "experience_score"),
        ("ATS Score", "ats_score"),
    ]
    c1, c2, c3, c4 = st.columns(4)
    for col, (label, key) in zip([c1, c2, c3, c4], sub_scores):
        val = int(float(ms.get(key, 0)))
        with col:
            st.metric(label, val)

    details = ms.get("details_json", {})

    tab_overview, tab_suggest = st.tabs(["Analysis", "Suggestions"])

    with tab_overview:
        if details.get("summary"):
            st.info(details["summary"])

        if details.get("matched_skills"):
            st.markdown("**Matched Skills**")
            st.write(", ".join(details["matched_skills"]))

        if details.get("missing_skills"):
            st.markdown("**Missing Skills**")
            st.write(", ".join(details["missing_skills"]))

        if details.get("strengths"):
            with st.expander("Strengths"):
                for item in details["strengths"]:
                    st.markdown(f"- {item}")

        if details.get("weaknesses"):
            with st.expander("Areas to Improve"):
                for item in details["weaknesses"]:
                    st.markdown(f"- {item}")

    with tab_suggest:
        with st.spinner("Generating suggestions..."):
            r_sug = api("POST", "/match/suggest", params={"resume_id": resume_id, "job_id": job_id})
        if r_sug and r_sug.ok:
            sug = r_sug.json()
            if isinstance(sug, dict):
                for section, items in sug.items():
                    st.markdown(f"**{section.replace('_', ' ').title()}**")
                    if isinstance(items, list):
                        for item in items:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(str(items))
            else:
                st.write(sug)
        else:
            st.info("Suggestions not available.")
