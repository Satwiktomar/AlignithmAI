import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_score_ring, render_empty_state, score_color



SVG_TARGET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>"""
SVG_DOC = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
SVG_CHAT = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>"""
SVG_BUILDING = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>"""
SVG_ROCKET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 2.18 0 0 0-2.91-.09z"></path><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path></svg>"""
SVG_WIFI = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>"""

def render():
    render_page_header("Match Report", "Score your resume against a job description")

    r_resumes = api("GET", "/resume/")
    r_jobs = api("GET", "/jobs/")

    if not r_resumes or not r_jobs:
        return

    resumes = r_resumes.json() if r_resumes.ok else []
    jobs = r_jobs.json() if r_jobs.ok else []

    if not resumes:
        render_empty_state(SVG_DOC, "No resumes uploaded", "Upload a resume first from the Resume page.")
        return
    if not jobs:
        render_empty_state(SVG_BUILDING, "No jobs added", "Analyze a job description first from the Jobs page.")
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
        run = st.button("Run Match Analysis", use_container_width=True)

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
<div style="background:#161925; border:1px solid #1e293b; border-radius:12px;
            padding:0.9rem; text-align:center;">
  <div style="font-size:1.6rem; font-weight:800; color:{color};">{int(val)}</div>
  <div style="font-size:0.72rem; color:#6b7280; text-transform:uppercase;
              letter-spacing:0.05em; margin-top:2px;">{label}</div>
</div>
""", unsafe_allow_html=True)

    details = ms.get("details_json", {})

    tab_overview, tab_suggest = st.tabs(["Analysis", "Suggestions"])

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
            with st.expander("Strengths"):
                for item in details["strengths"]:
                    st.markdown(f"• {item}")

        if details.get("weaknesses"):
            with st.expander("Areas to Improve"):
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
