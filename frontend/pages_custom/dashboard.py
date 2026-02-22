import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_stat_card, render_empty_state, score_color



SVG_TARGET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>"""
SVG_DOC = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
SVG_CHAT = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>"""
SVG_BUILDING = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>"""
SVG_ROCKET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 2.18 0 0 0-2.91-.09z"></path><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path></svg>"""
SVG_WIFI = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>"""

def render():
    render_page_header("Dashboard", "Your career activity at a glance")

    r = api("GET", "/advanced/dashboard-stats")
    if not r or r.status_code != 200:
        render_empty_state(SVG_WIFI, "Couldn't load stats", "Make sure the API server is running.")
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
                "",
                "Welcome to Alignithm.AI",
                "Upload your resume and add a job description to get your first match score."
            )
        else:
            render_empty_state(
                "",
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
