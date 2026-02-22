import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state, score_color


def render():
    render_page_header("Skill Gap Analysis", "Identify gaps and get a personalized learning path")

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

    if st.button("📊 Analyze Skill Gap", use_container_width=True):
        with st.spinner("Mapping your skill gaps…"):
            r = api("POST", "/advanced/skillgap", params={"resume_id": resume_opts[sel_r], "job_id": job_opts[sel_j]})
        if r and r.ok:
            st.session_state["skillgap_result"] = r.json()
        elif r:
            st.error(r.json().get("detail", "Analysis failed."))

    result = st.session_state.get("skillgap_result")
    if not result:
        return

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    if result.get("missing_skills"):
        st.markdown("#### Skills to Acquire")
        pills = "".join(f'<span class="badge badge-missing">{s}</span>' for s in result["missing_skills"])
        st.markdown(f"<div style='margin-bottom:1rem'>{pills}</div>", unsafe_allow_html=True)

    if result.get("matched_skills"):
        st.markdown("#### Skills You Already Have")
        pills = "".join(f'<span class="badge badge-matched">{s}</span>' for s in result["matched_skills"])
        st.markdown(f"<div style='margin-bottom:1rem'>{pills}</div>", unsafe_allow_html=True)

    if result.get("learning_roadmap"):
        st.markdown("#### 📍 Learning Roadmap")
        for i, step in enumerate(result["learning_roadmap"], 1):
            if isinstance(step, dict):
                skill = step.get("skill", "")
                action = step.get("action", step.get("resource", ""))
                timeline = step.get("timeline", "")
                st.markdown(f"""
<div class="info-card" style="margin-bottom:0.5rem">
  <div style="font-weight:600; color:#e8eaf0">{i}. {skill}</div>
  <div style="color:#9aa3b8; font-size:0.85rem; margin-top:4px">{action}</div>
  {f'<div style="color:#6b7280; font-size:0.78rem; margin-top:4px">⏱ {timeline}</div>' if timeline else ''}
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown(f"**{i}.** {step}")

    if result.get("certifications"):
        st.markdown("#### 🎓 Recommended Certifications")
        for cert in result["certifications"]:
            if isinstance(cert, dict):
                name = cert.get("name", "")
                provider = cert.get("provider", "")
                url = cert.get("url", "")
                link = f"[{name}]({url})" if url else name
                st.markdown(f"- {link}" + (f" — *{provider}*" if provider else ""))
            else:
                st.markdown(f"- {cert}")
