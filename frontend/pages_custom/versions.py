import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state, score_color


def render():
    render_page_header("Resume Versions", "Save and compare tailored resume versions for each job")

    tab_save, tab_compare = st.tabs(["Save Version", "Compare Versions"])

    with tab_save:
        r_res = api("GET", "/resume/")
        r_jobs = api("GET", "/jobs/")
        if not r_res or not r_jobs:
            return

        resumes = r_res.json() if r_res.ok else []
        jobs = r_jobs.json() if r_jobs.ok else []

        if not resumes:
            render_empty_state(None, "No resumes", "Upload a resume first.")
            return

        resume_opts = {f"{r.get('original_filename', 'Resume')} (#{r['id']})": r["id"] for r in resumes}
        job_opts = {"None": None}
        job_opts.update({f"{j.get('job_title', 'Job')} @ {j.get('company_name', '?')} (#{j['id']})": j["id"] for j in jobs})

        sel_r = st.selectbox("Resume to snapshot", list(resume_opts.keys()))
        sel_j = st.selectbox("Target job (optional)", list(job_opts.keys()))
        label = st.text_input("Version label", placeholder="e.g. ML Engineer v2")
        notes = st.text_area("Notes", height=80, placeholder="What changed in this version?")

        if st.button("Save Version", use_container_width=True):
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
        r_res = api("GET", "/resume/")
        if not r_res or not r_res.ok:
            st.error("Failed to load resumes.")
            return
        resumes = r_res.json()
        if not resumes:
            render_empty_state(None, "No resumes", "Upload a resume first.")
            return

        resume_opts = {f"{r.get('original_filename', 'Resume')} (#{r['id']})": r["id"] for r in resumes}
        sel_r = st.selectbox("Resume", list(resume_opts.keys()), key="ver_sel_r")

        r_vers = api("GET", f"/resume/{resume_opts[sel_r]}/versions")
        if not r_vers or not r_vers.ok:
            st.error("Failed to load versions.")
            return
        versions = r_vers.json()
        if not versions:
            render_empty_state(None, "No saved versions", "Save your first version in the 'Save Version' tab.")
            return

        for v in versions:
            score = v.get("match_score")
            date = str(v.get("created_at", ""))[:10]
            label_str = v.get("version_label", "Untitled")
            score_str = f"  |  Score: {int(float(score))}" if score is not None else ""

            with st.expander(f"{label_str}  |  {date}{score_str}"):
                if v.get("notes"):
                    st.caption(v["notes"])
                content = v.get("content_json", {})
                if content:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Name:** {content.get('name', '—')}")
                        st.markdown(f"**Title:** {content.get('current_title', '') or content.get('title', '—')}")
                    with c2:
                        skills_all = content.get("skills", {})
                        if isinstance(skills_all, dict):
                            all_skills = []
                            for lst in skills_all.values():
                                all_skills.extend(lst or [])
                        else:
                            all_skills = skills_all or []
                        if all_skills:
                            st.markdown(f"**Skills:** {', '.join(all_skills[:8])}")
                if st.button("Delete", key=f"del_ver_{v['id']}"):
                    dr = api("DELETE", f"/resume/version/{v['id']}")
                    if dr and dr.ok:
                        st.rerun()
