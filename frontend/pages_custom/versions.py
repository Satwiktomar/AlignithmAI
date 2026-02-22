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
    render_page_header("Resume Versions", "Save and compare tailored resume versions for each job")

    tab_save, tab_compare = st.tabs(["Save Version", "Compare Versions"])

    with tab_save:
        st.markdown("<br>", unsafe_allow_html=True)
        r_res = api("GET", "/resume/")
        r_jobs = api("GET", "/jobs/")
        if not r_res or not r_jobs:
            return

        resumes = r_res.json() if r_res.ok else []
        jobs = r_jobs.json() if r_jobs.ok else []

        if not resumes:
            render_empty_state(SVG_DOC, "No resumes", "Upload a resume first.")
            return

        resume_opts = {f"{r.get('original_filename','Resume')} (#{r['id']})": r["id"] for r in resumes}
        job_opts = {"None": None}
        job_opts.update({f"{j.get('job_title','Job')} @ {j.get('company_name','?')} (#{j['id']})": j["id"] for j in jobs})

        sel_r = st.selectbox("Resume to snapshot", list(resume_opts.keys()))
        sel_j = st.selectbox("Target job (optional)", list(job_opts.keys()))
        label = st.text_input("Version label", placeholder="e.g. ML Engineer v2 — January 2025")
        notes = st.text_area("Notes", height=80, placeholder="What changed in this version?")

        if st.button("💾 Save Version", use_container_width=True):
            if not label:
                st.error("Please give this version a label.")
            else:
                r = api("POST", "/resume/version", json={
                    "resume_id": resume_opts[sel_r],
                    "job_id": job_opts[sel_j],
                    "version_label": label,
                    "notes": notes
                })
                if r and r.ok:
                    st.success("Version saved.")
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Save failed."))

    with tab_compare:
        st.markdown("<br>", unsafe_allow_html=True)
        r_res = api("GET", "/resume/")
        if not r_res or not r_res.ok:
            st.error("Failed to load resumes.")
            return
        resumes = r_res.json()
        if not resumes:
            render_empty_state(SVG_DOC, "No resumes", "Upload a resume first.")
            return

        resume_opts = {f"{r.get('original_filename','Resume')} (#{r['id']})": r["id"] for r in resumes}
        sel_r = st.selectbox("Resume", list(resume_opts.keys()), key="ver_sel_r")

        r_vers = api("GET", f"/resume/{resume_opts[sel_r]}/versions")
        if not r_vers or not r_vers.ok:
            st.error("Failed to load versions.")
            return
        versions = r_vers.json()
        if not versions:
            render_empty_state(SVG_DOC, "No saved versions", "Save your first version in the 'Save Version' tab.")
            return

        for v in versions:
            score = v.get("match_score")
            date = str(v.get("created_at", ""))[:10]
            score_html = ""
            if score is not None:
                color = score_color(float(score))
                score_html = f'<span style="color:{color}; font-weight:700; font-size:1rem">{int(score)}</span> match'

            with st.expander(f"{v.get('version_label','Untitled')}  ·  {date}  {score_html if score else ''}"):
                if v.get("notes"):
                    st.markdown(f"*{v['notes']}*")
                content = v.get("content_json", {})
                if content:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Name:** {content.get('name','—')}")
                        st.markdown(f"**Title:** {content.get('current_title','') or content.get('title','—')}")
                    with c2:
                        skills_all = content.get("skills", {})
                        if isinstance(skills_all, dict):
                            all_skills = []
                            for lst in skills_all.values():
                                all_skills.extend(lst or [])
                        else:
                            all_skills = skills_all or []
                        if all_skills:
                            pills = "".join(f'<span class="badge badge-skill">{s}</span>' for s in all_skills[:8])
                            st.markdown(f"<div>{pills}</div>", unsafe_allow_html=True)
                if st.button("Delete", key=f"del_ver_{v['id']}"):
                    dr = api("DELETE", f"/resume/version/{v['id']}")
                    if dr and dr.ok:
                        st.rerun()
