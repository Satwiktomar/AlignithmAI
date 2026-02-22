import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


TONE_OPTIONS = ["formal", "semi-formal", "startup", "direct", "corporate"]
TONE_LABELS = {
    "formal": "🎩 Formal",
    "semi-formal": "👔 Semi-Formal",
    "startup": "Startup Energy",
    "direct": "Direct & Punchy",
    "corporate": "🏢 Corporate"
}



SVG_TARGET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>"""
SVG_DOC = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
SVG_CHAT = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>"""
SVG_BUILDING = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>"""
SVG_ROCKET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 2.18 0 0 0-2.91-.09z"></path><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path></svg>"""
SVG_WIFI = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>"""

def render():
    render_page_header("Cover Letter Generator", "AI-crafted letters tailored to each job")

    tab_gen, tab_saved = st.tabs(["Generate", "Saved Letters"])

    with tab_gen:
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

        tone = st.selectbox("Tone", TONE_OPTIONS, format_func=lambda x: TONE_LABELS.get(x, x))

        if st.button("️ Generate Cover Letter", use_container_width=True):
            with st.spinner("Writing your cover letter…"):
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
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='info-card'>{cl.get('generated_text','').replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button("⬇️ Download .txt", cl.get("generated_text",""), file_name="cover_letter.txt", use_container_width=True)
            with col_b:
                if st.button("Copy to Clipboard", use_container_width=True):
                    st.write("Copied! (Select all text above and copy manually.)")

    with tab_saved:
        st.markdown("<br>", unsafe_allow_html=True)
        r = api("GET", "/coverletter/")
        if not r or not r.ok:
            st.error("Failed to load cover letters.")
            return
        letters = r.json()
        if not letters:
            render_empty_state(SVG_DOC, "No saved letters", "Generate your first cover letter above.")
            return

        for cl in letters:
            date = str(cl.get("created_at",""))[:10]
            tone_label = TONE_LABELS.get(cl.get("tone",""), cl.get("tone",""))
            with st.expander(f"{tone_label}  ·  {date}"):
                st.write(cl.get("generated_text",""))
                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button("⬇️ Download", cl.get("generated_text",""), file_name=f"cover_letter_{cl['id']}.txt", use_container_width=True)
                with col_b:
                    if st.button("Delete", key=f"del_cl_{cl['id']}", use_container_width=True):
                        dr = api("DELETE", f"/coverletter/{cl['id']}")
                        if dr and dr.ok:
                            st.rerun()
