import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_stat_card, render_empty_state, score_color


@st.cache_data(ttl=60, show_spinner=False)
def fetch_dashboard_stats(token):
    from utils.auth import api
    r = api("GET", "/advanced/dashboard-stats")
    if r and r.ok:
        return r.json()
    return None


def render():
    render_page_header("Dashboard", "Your career activity at a glance")

    token = st.session_state.get("token")
    stats = fetch_dashboard_stats(token)

    if not stats:
        render_empty_state(None, "Could not load stats", "Make sure the API server is running.")
        return

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

    st.markdown("---")

    if not recent:
        if resumes == 0:
            render_empty_state(None, "Welcome to Alignithm.AI",
                               "Upload your resume and add a job description to get your first match score.")
        else:
            render_empty_state(None, "No match history yet",
                               "Go to the Match tab, select a resume and a job, and run your first analysis.")
        return

    st.markdown("#### Recent Match Scores")

    r_resumes = api("GET", "/resume/")
    r_jobs = api("GET", "/jobs/")
    resume_map = {
        r_obj["id"]: r_obj.get("original_filename", f"Resume #{r_obj['id']}")
        for r_obj in (r_resumes.json() if r_resumes and r_resumes.ok else [])
    }
    job_map = {
        j["id"]: f"{j.get('job_title','') or ''} @ {j.get('company_name','') or ''}".strip(" @")
        for j in (r_jobs.json() if r_jobs and r_jobs.ok else [])
    }

    for ms in recent:
        score = ms.get("overall_score", 0)
        color = score_color(score)
        resume_label = resume_map.get(ms.get("resume_id"), f"Resume #{ms.get('resume_id')}")
        job_label = job_map.get(ms.get("job_id"), f"Job #{ms.get('job_id')}")
        created = ms.get("created_at", "")[:10]

        st.markdown(
            f"**{int(score)}** — {job_label or 'Unnamed Job'} · {resume_label} · {created}"
        )
