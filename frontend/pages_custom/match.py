import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_score_ring, render_empty_state, score_color


def render():
    render_page_header("Match Report", "Score your resume against a job description")

    r_resumes = api("GET", "/resume/")
    r_jobs = api("GET", "/jobs/")

    if not r_resumes or not r_jobs:
        return

    resumes = r_resumes.json() if r_resumes.ok else []
    jobs = r_jobs.json() if r_jobs.ok else []

    if not resumes:
        render_empty_state("📄", "No resumes uploaded", "Upload a resume first from the Resume page.")
        return
    if not jobs:
        render_empty_state("💼", "No jobs added", "Analyze a job description first from the Jobs page.")
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

    st.markdown("<br>", unsafe_allow_html=True)

    col_run, _ = st.columns([1, 3])
    with col_run:
        run = st.button("⚡ Run Match Analysis", use_container_width=True)

    if run:
        with st.spinner("Analyzing your fit…"):
            r = api("POST", "/match/", params={"resume_id": resume_id, "job_id": job_id})
        if not r or not r.ok:
            st.error(r.json().get("detail", "Match analysis failed.") if r else "API error.")
            return
        ms = r.json()
        st.session_state["last_match"] = ms

    ms = st.session_state.get("last_match")
    if not ms:
        return

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    render_score_ring(float(ms.get("overall_score", 0)), "Overall")

    c1, c2, c3, c4 = st.columns(4)
    sub_scores = [
        ("Skill Match", "skill_score"),
        ("Keyword", "keyword_score"),
        ("Experience", "experience_score"),
        ("ATS Score", "ats_score"),
    ]
    for col, (label, key) in zip([c1, c2, c3, c4], sub_scores):
        val = float(ms.get(key, 0))
        color = score_color(val)
        with col:
            st.markdown(f"""
<div style="background:#13161e; border:1px solid #1e2130; border-radius:12px;
            padding:0.9rem; text-align:center;">
  <div style="font-size:1.6rem; font-weight:800; color:{color};">{int(val)}</div>
  <div style="font-size:0.72rem; color:#6b7280; text-transform:uppercase;
              letter-spacing:0.05em; margin-top:2px;">{label}</div>
</div>
""", unsafe_allow_html=True)

    details = ms.get("details_json", {})

    tab_overview, tab_suggest = st.tabs(["📋 Analysis", "💡 Suggestions"])

    with tab_overview:
        st.markdown("<br>", unsafe_allow_html=True)
        if details.get("summary"):
            st.info(details["summary"])

        if details.get("matched_skills"):
            st.markdown("**Matched Skills**")
            skills_html = "".join(f'<span class="badge badge-matched">{s}</span>' for s in details["matched_skills"])
            st.markdown(f'<div style="margin-bottom:0.8rem">{skills_html}</div>', unsafe_allow_html=True)

        if details.get("missing_skills"):
            st.markdown("**Missing Skills**")
            skills_html = "".join(f'<span class="badge badge-missing">{s}</span>' for s in details["missing_skills"])
            st.markdown(f'<div style="margin-bottom:0.8rem">{skills_html}</div>', unsafe_allow_html=True)

        if details.get("strengths"):
            with st.expander("✅ Strengths"):
                for item in details["strengths"]:
                    st.markdown(f"• {item}")

        if details.get("weaknesses"):
            with st.expander("⚠️ Areas to Improve"):
                for item in details["weaknesses"]:
                    st.markdown(f"• {item}")

    with tab_suggest:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.spinner("Generating improvement suggestions…"):
            r_sug = api("POST", "/match/suggest", params={"resume_id": resume_id, "job_id": job_id})
        if r_sug and r_sug.ok:
            sug = r_sug.json()
            if isinstance(sug, dict):
                for section, items in sug.items():
                    st.markdown(f"**{section.replace('_',' ').title()}**")
                    if isinstance(items, list):
                        for item in items:
                            st.markdown(f"• {item}")
                    else:
                        st.markdown(str(items))
                    st.markdown("")
            else:
                st.write(sug)
        else:
            st.info("Suggestions not available.")
