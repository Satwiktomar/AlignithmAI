import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


def render():
    render_page_header("Projects", "Showcase your work and find which projects to highlight")

    tab_list, tab_add, tab_rank = st.tabs(["My Projects", "Add Project", "Rank for Job"])

    with tab_add:
        st.markdown("<br>", unsafe_allow_html=True)
        title = st.text_input("Project title")
        description = st.text_area("Description", height=100, placeholder="What did you build and why?")
        domain = st.text_input("Domain", placeholder="e.g. Machine Learning, Web Dev, DevOps")
        skills_raw = st.text_input("Skills used (comma-separated)", placeholder="Python, FastAPI, PostgreSQL")
        metrics_raw = st.text_input("Key metrics (comma-separated)", placeholder="Reduced latency by 40%, 10k users")
        github_url = st.text_input("GitHub URL (optional)")
        complexity = st.selectbox("Complexity level", ["Beginner", "Intermediate", "Advanced"])

        if st.button("➕ Add Project", use_container_width=True):
            if not title:
                st.error("Project title is required.")
            else:
                skills_list = [s.strip() for s in skills_raw.split(",") if s.strip()]
                metrics_list = [m.strip() for m in metrics_raw.split(",") if m.strip()]
                r = api("POST", "/projects/", json={
                    "title": title,
                    "description": description,
                    "domain": domain,
                    "skills_json": skills_list,
                    "metrics_json": metrics_list,
                    "github_url": github_url,
                    "complexity_level": complexity,
                    "tags": []
                })
                if r and r.ok:
                    st.success("✅ Project added.")
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Failed to add project."))

    with tab_list:
        st.markdown("<br>", unsafe_allow_html=True)
        r = api("GET", "/projects/")
        if not r or not r.ok:
            st.error("Failed to load projects.")
            return
        projects = r.json()
        if not projects:
            render_empty_state("🗂️", "No projects yet", "Add your first project in the 'Add Project' tab.")
            return

        for p in projects:
            with st.expander(f"🗂️ {p.get('title','')}  ·  {p.get('domain','') or 'General'}"):
                if p.get("description"):
                    st.write(p["description"])
                if p.get("skills_json"):
                    pills = "".join(f'<span class="badge badge-skill">{s}</span>' for s in p["skills_json"])
                    st.markdown(f"<div style='margin-bottom:0.4rem'>{pills}</div>", unsafe_allow_html=True)
                if p.get("metrics_json"):
                    st.markdown(f"**Metrics:** {' | '.join(p['metrics_json'])}")
                if p.get("github_url"):
                    st.markdown(f"[🔗 GitHub]({p['github_url']})")
                if st.button("🗑️ Delete", key=f"del_proj_{p['id']}"):
                    dr = api("DELETE", f"/projects/{p['id']}")
                    if dr and dr.ok:
                        st.rerun()

    with tab_rank:
        st.markdown("<br>", unsafe_allow_html=True)
        r_jobs = api("GET", "/jobs/")
        if not r_jobs or not r_jobs.ok:
            st.error("Failed to load jobs.")
            return
        jobs = r_jobs.json()
        if not jobs:
            render_empty_state("💼", "No jobs", "Add a job description first.")
            return

        job_opts = {f"{j.get('job_title','Job')} @ {j.get('company_name','?')} (#{j['id']})": j["id"] for j in jobs}
        sel_j = st.selectbox("Select job to rank projects against", list(job_opts.keys()))

        if st.button("🏆 Rank My Projects", use_container_width=True):
            with st.spinner("Ranking projects by relevance…"):
                r = api("POST", "/projects/recommend", params={"job_id": job_opts[sel_j]})
            if r and r.ok:
                st.session_state["ranked_projects"] = r.json()
            elif r:
                st.error(r.json().get("detail", "Ranking failed."))

        ranked = st.session_state.get("ranked_projects")
        if ranked:
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            items = ranked if isinstance(ranked, list) else ranked.get("ranked", ranked.get("projects", []))
            for i, p in enumerate(items, 1):
                score = p.get("relevance_score", p.get("score", 0))
                from utils.styles import score_color
                color = score_color(float(score))
                st.markdown(f"""
<div class="info-card" style="display:flex; align-items:center; gap:1rem; margin-bottom:0.5rem">
  <div style="font-size:1.4rem; font-weight:800; color:{color}; min-width:40px">#{i}</div>
  <div style="flex:1">
    <div style="font-weight:600">{p.get('title','Project')}</div>
    <div style="font-size:0.8rem; color:#6b7280">{p.get('reason','') or p.get('rationale','')}</div>
  </div>
  <div style="font-size:1.2rem; font-weight:700; color:{color}">{int(score)}</div>
</div>
""", unsafe_allow_html=True)
