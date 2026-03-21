import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


def render():
    render_page_header("Project Manager", "Extract, rank, and showcase your projects")

    tab_extract, tab_list, tab_rank = st.tabs(["GitHub Extract", "My Projects", "Rank"])

    with tab_extract:
        st.markdown("""
<div style="font-size:0.85rem;color:#8B8BA8;font-family:'Inter',sans-serif;margin-bottom:0.8rem;">
  Paste structured GitHub contribution data to extract projects
</div>
""", unsafe_allow_html=True)

        raw = st.text_area("GitHub data / project description", height=180,
                           placeholder="Paste your GitHub contributions, project descriptions, or raw data here...")
        if st.button("🚀 Extract Projects", use_container_width=True):
            if not raw.strip():
                st.error("Please paste some project data.")
            else:
                with st.spinner("Extracting projects with AI..."):
                    r = api("POST", "/projects/extract", timeout=600, json={"raw_text": raw})
                if r and r.ok:
                    st.success("✅ Projects extracted and saved!")
                    st.rerun()
                elif r:
                    detail = ""
                    try:
                        detail = r.json().get("detail", "")
                    except Exception:
                        detail = f"HTTP {r.status_code}"
                    st.error(detail or "Extraction failed.")

    with tab_list:
        r = api("GET", "/projects/")
        if not r or not r.ok:
            st.error("Failed to load projects.")
            return
        projects = r.json()
        if not projects:
            render_empty_state(None, "No projects yet", "Use the GitHub Extract tab to add projects.")
            return

        for proj in projects:
            name = proj.get("name") or proj.get("title", f"Project #{proj['id']}")
            domain = proj.get("domain", "")

            header_parts = [f"🚀 {name}"]
            if domain:
                header_parts.append(f"[{domain}]")

            with st.expander(" · ".join(header_parts)):
                description = proj.get("description", "")
                if description:
                    st.markdown(f"""
<div style="font-size:0.85rem;color:#B0B0CC;line-height:1.6;font-family:'Inter',sans-serif;
            margin-bottom:0.6rem;">
  {description[:400]}{'...' if len(description) > 400 else ''}
</div>
""", unsafe_allow_html=True)

                # ── Skills / Technologies ──
                skills = proj.get("skills") or proj.get("technologies") or []
                if skills:
                    if isinstance(skills, str):
                        skills = [s.strip() for s in skills.split(",") if s.strip()]
                    badges = ""
                    for sk in skills[:8]:
                        badges += (
                            f'<span style="display:inline-block;padding:0.18rem 0.6rem;'
                            f'border-radius:16px;font-size:0.72rem;font-weight:600;'
                            f'background:rgba(99,102,241,0.12);color:#A5B4FC;'
                            f'border:1px solid rgba(99,102,241,0.25);margin:2px;'
                            f'font-family:\'Inter\',sans-serif;">{sk}</span>'
                        )
                    st.markdown(f"""
<div style="margin-top:0.3rem;">
  <div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
              font-weight:600;margin-bottom:0.3rem;font-family:'Inter',sans-serif;">Technologies</div>
  {badges}
</div>
""", unsafe_allow_html=True)

                # ── Metrics ──
                metrics = proj.get("metrics") or {}
                if metrics:
                    m_parts = []
                    for k, v in list(metrics.items())[:4]:
                        m_parts.append(f"<strong>{k.replace('_',' ').title()}:</strong> {v}")
                    if m_parts:
                        st.markdown(f"""
<div style="background:rgba(19,19,43,0.4);border-radius:8px;padding:0.5rem 0.8rem;
            margin-top:0.5rem;font-size:0.78rem;color:#8B8BA8;
            font-family:'Inter',sans-serif;">
  {' &nbsp;·&nbsp; '.join(m_parts)}
</div>
""", unsafe_allow_html=True)

                # ── LaTeX ──
                latex = proj.get("latex_snippet", "")
                if latex:
                    with st.expander("📝 LaTeX Snippet"):
                        st.code(latex, language="latex")

                st.markdown('<div style="height:0.3rem;"></div>', unsafe_allow_html=True)
                if st.button("🗑 Delete", key=f"del_proj_{proj['id']}",
                             use_container_width=True):
                    dr = api("DELETE", f"/projects/{proj['id']}")
                    if dr and dr.ok:
                        st.rerun()

    with tab_rank:
        r_proj = api("GET", "/projects/")
        r_jobs = api("GET", "/jobs/")
        if not r_proj or not r_jobs:
            return
        projects = r_proj.json() if r_proj.ok else []
        jobs = r_jobs.json() if r_jobs.ok else []

        if not projects:
            render_empty_state(None, "No projects to rank", "Add projects first.")
            return
        if not jobs:
            render_empty_state(None, "No jobs", "Add a job to rank projects against.")
            return

        job_opts = {f"{j.get('job_title', 'Job')} (#{j['id']})": j["id"] for j in jobs}
        sel_j = st.selectbox("Rank against job", list(job_opts.keys()), key="rank_job")

        if st.button("📊 Rank Projects", use_container_width=True):
            with st.spinner("Ranking projects for job relevance..."):
                r = api("POST", "/projects/rank", timeout=600, json={"job_id": job_opts[sel_j]})
            if r and r.ok:
                st.session_state["rank_result"] = r.json()
            elif r:
                st.error("Ranking failed.")

        ranked = st.session_state.get("rank_result")
        if ranked:
            results = ranked if isinstance(ranked, list) else ranked.get("rankings", [])
            for idx, item in enumerate(results):
                score = float(item.get("score", item.get("relevance_score", 0)))
                name = item.get("name", item.get("project_name", f"Project {idx + 1}"))
                reason = item.get("reason", item.get("explanation", ""))
                from utils.styles import score_color
                color = score_color(score)
                st.markdown(f"""
<div style="background:rgba(19,19,43,0.5);border:1px solid rgba(139,92,246,0.1);
            border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.4rem;
            display:flex;align-items:center;gap:0.8rem;backdrop-filter:blur(6px);">
  <div style="background:{color}18;border:1px solid {color}40;border-radius:8px;
              padding:0.3rem 0.6rem;font-size:0.9rem;font-weight:700;color:{color};
              font-family:'Inter',sans-serif;min-width:40px;text-align:center;">
    {int(score)}
  </div>
  <div style="flex:1;">
    <div style="font-size:0.85rem;font-weight:600;color:#E8E8F0;font-family:'Inter',sans-serif;">
      {name}
    </div>
    <div style="font-size:0.75rem;color:#8B8BA8;font-family:'Inter',sans-serif;">
      {reason}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
