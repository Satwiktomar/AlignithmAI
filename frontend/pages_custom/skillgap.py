import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state, score_color



SVG_TARGET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>"""
SVG_DOC = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
SVG_CHAT = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>"""
SVG_BUILDING = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>"""
SVG_ROCKET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 2.18 0 0 0-2.91-.09z"></path><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path></svg>"""
SVG_WIFI = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>"""

def render():
    render_page_header("Skill Gap Analysis", "Identify gaps and get a personalized learning path")

    r_res = api("GET", "/resume/")
    r_jobs = api("GET", "/jobs/")
    if not r_res or not r_jobs:
        return

    resumes = r_res.json() if r_res.ok else []
    jobs = r_jobs.json() if r_jobs.ok else []

    if not resumes:
        render_empty_state(SVG_DOC, "No resumes", "Upload a resume first.")
        return
    if not jobs:
        render_empty_state(SVG_BUILDING, "No jobs", "Add a job description first.")
        return

    c1, c2 = st.columns(2)
    with c1:
        resume_opts = {f"{r.get('original_filename','Resume')} (#{r['id']})": r["id"] for r in resumes}
        sel_r = st.selectbox("Resume", list(resume_opts.keys()))
    with c2:
        job_opts = {f"{j.get('job_title','Job')} @ {j.get('company_name','?')} (#{j['id']})": j["id"] for j in jobs}
        sel_j = st.selectbox("Job", list(job_opts.keys()))

    if st.button("Analyze Skill Gap", use_container_width=True):
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
