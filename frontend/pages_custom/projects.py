import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state



SVG_TARGET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>"""
SVG_DOC = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
SVG_CHAT = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>"""
SVG_BUILDING = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>"""
SVG_ROCKET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 2.18 0 0 0-2.91-.09z"></path><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path></svg>"""
SVG_WIFI = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>"""

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
                    st.success("Project added.")
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
            render_empty_state(SVG_DOC, "No projects yet", "Add your first project in the 'Add Project' tab.")
            return

        for p in projects:
            with st.expander(f"{p.get('title','')}  ·  {p.get('domain','') or 'General'}"):
                if p.get("description"):
                    st.write(p["description"])
                if p.get("skills_json"):
                    pills = "".join(f'<span class="badge badge-skill">{s}</span>' for s in p["skills_json"])
                    st.markdown(f"<div style='margin-bottom:0.4rem'>{pills}</div>", unsafe_allow_html=True)
                if p.get("metrics_json"):
                    st.markdown(f"**Metrics:** {' | '.join(p['metrics_json'])}")
                if p.get("github_url"):
                    st.markdown(f"[🔗 GitHub]({p['github_url']})")
                if st.button("Delete", key=f"del_proj_{p['id']}"):
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
            render_empty_state(SVG_BUILDING, "No jobs", "Add a job description first.")
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
