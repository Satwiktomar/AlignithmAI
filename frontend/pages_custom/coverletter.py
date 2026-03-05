import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


TONE_OPTIONS = ["formal", "semi-formal", "startup", "direct", "corporate"]
TONE_LABELS = {
    "formal": "Formal",
    "semi-formal": "Semi-Formal",
    "startup": "Startup",
    "direct": "Direct",
    "corporate": "Corporate",
}


def render():
    render_page_header("Cover Letter Generator", "AI-crafted letters tailored to each job")

    tab_gen, tab_saved = st.tabs(["Generate", "Saved Letters"])

    with tab_gen:
        r_res = api("GET", "/resume/")
        r_jobs = api("GET", "/jobs/")
        if not r_res or not r_jobs:
            return

        resumes = r_res.json() if r_res.ok else []
        jobs = r_jobs.json() if r_jobs.ok else []

        if not resumes:
            render_empty_state(None, "No resumes", "Upload a resume first.")
            return
        if not jobs:
            render_empty_state(None, "No jobs", "Add a job description first.")
            return

        c1, c2 = st.columns(2)
        with c1:
            resume_opts = {f"{r.get('original_filename', 'Resume')} (#{r['id']})": r["id"] for r in resumes}
            sel_r = st.selectbox("Resume", list(resume_opts.keys()))
        with c2:
            job_opts = {f"{j.get('job_title', 'Job')} @ {j.get('company_name', '?')} (#{j['id']})": j["id"] for j in jobs}
            sel_j = st.selectbox("Job", list(job_opts.keys()))

        tone = st.selectbox("Tone", TONE_OPTIONS, format_func=lambda x: TONE_LABELS.get(x, x))

        if st.button("Generate Cover Letter", use_container_width=True):
            with st.spinner("Generating cover letter..."):
                r = api("POST", "/coverletter/generate", json={
                    "resume_id": resume_opts[sel_r],
                    "job_id": job_opts[sel_j],
                    "tone": tone
                })
            if r and r.ok:
                st.session_state["last_cl"] = r.json()
            elif r:
                st.error(r.json().get("detail", "Generation failed."))

        cl = st.session_state.get("last_cl")
        if cl:
            st.markdown("---")
            st.text_area("Generated Cover Letter", cl.get("generated_text", ""), height=300)
            st.download_button("Download as .txt", cl.get("generated_text", ""), file_name="cover_letter.txt")

    with tab_saved:
        r = api("GET", "/coverletter/")
        if not r or not r.ok:
            st.error("Failed to load cover letters.")
            return
        letters = r.json()
        if not letters:
            render_empty_state(None, "No saved letters", "Generate your first cover letter above.")
            return

        for cl in letters:
            date = str(cl.get("created_at", ""))[:10]
            tone_label = TONE_LABELS.get(cl.get("tone", ""), cl.get("tone", ""))
            with st.expander(f"{tone_label}  |  {date}"):
                st.text_area("", cl.get("generated_text", ""), height=200, key=f"cl_text_{cl['id']}")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button("Download", cl.get("generated_text", ""),
                                       file_name=f"cover_letter_{cl['id']}.txt",
                                       key=f"dl_cl_{cl['id']}")
                with col_b:
                    if st.button("Delete", key=f"del_cl_{cl['id']}", use_container_width=True):
                        dr = api("DELETE", f"/coverletter/{cl['id']}")
                        if dr and dr.ok:
                            st.rerun()
