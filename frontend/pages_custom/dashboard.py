import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_stat_card, render_empty_state, score_color


def render():
    render_page_header("Dashboard", "Your career activity at a glance")

    r = api("GET", "/advanced/dashboard-stats")
    if not r or r.status_code != 200:
        render_empty_state("📡", "Couldn't load stats", "Make sure the API server is running.")
        return

    stats = r.json()
    resumes = stats.get("resumes", 0)
    jobs = stats.get("jobs", 0)
    projects = stats.get("projects", 0)
    cls = stats.get("cover_letters", 0)
    recent = stats.get("recent_matches", [])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card(resumes, "Resumes")
    with c2:
        render_stat_card(jobs, "Jobs Analyzed")
    with c3:
        render_stat_card(projects, "Projects")
    with c4:
        render_stat_card(cls, "Cover Letters")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    if not recent:
        if resumes == 0:
            render_empty_state(
                "🚀",
                "Welcome to RoleFit AI",
                "Upload your resume and add a job description to get your first match score."
            )
        else:
            render_empty_state(
                "🎯",
                "No match history yet",
                "Go to the Match tab, select a resume and a job, and run your first analysis."
            )
        return

    st.markdown("#### Recent Match Scores")

    r_resumes = api("GET", "/resume/")
    r_jobs = api("GET", "/jobs/")
    resume_map = {r_obj["id"]: r_obj.get("original_filename", f"Resume #{r_obj['id']}") for r_obj in (r_resumes.json() if r_resumes and r_resumes.ok else [])}
    job_map = {j["id"]: f"{j.get('job_title','') or ''} @ {j.get('company_name','') or ''}".strip(" @") for j in (r_jobs.json() if r_jobs and r_jobs.ok else [])}

    for ms in recent:
        score = ms.get("overall_score", 0)
        color = score_color(score)
        resume_label = resume_map.get(ms.get("resume_id"), f"Resume #{ms.get('resume_id')}")
        job_label = job_map.get(ms.get("job_id"), f"Job #{ms.get('job_id')}")
        created = ms.get("created_at", "")[:10]

        st.markdown(f"""
<div class="match-row">
  <div style="width:52px; height:52px; border-radius:50%; border:3px solid {color};
              display:flex; align-items:center; justify-content:center; flex-shrink:0;
              font-size:1.1rem; font-weight:800; color:{color};">
    {int(score)}
  </div>
  <div style="margin-left:1rem; flex:1; min-width:0;">
    <div style="font-weight:600; font-size:0.9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
      {job_label or "Unnamed Job"}
    </div>
    <div style="font-size:0.78rem; color:#6b7280; margin-top:2px;">
      {resume_label} &nbsp;·&nbsp; {created}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
