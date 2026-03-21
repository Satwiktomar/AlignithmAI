import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


def render():
    render_page_header("Cover Letter Generator", "AI-crafted cover letters tailored to each job")

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

    tab_gen, tab_saved = st.tabs(["Generate", "Saved Letters"])

    with tab_gen:
        c1, c2 = st.columns(2)
        with c1:
            resume_opts = {f"{r.get('original_filename', 'Resume')} (#{r['id']})": r["id"] for r in resumes}
            sel_r = st.selectbox("Resume", list(resume_opts.keys()), key="cl_resume")
        with c2:
            job_opts = {f"{j.get('job_title', 'Job')} @ {j.get('company_name', '?')} (#{j['id']})": j["id"] for j in jobs}
            sel_j = st.selectbox("Job", list(job_opts.keys()), key="cl_job")

        # ── Tone Selector ──
        st.markdown("""
<div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
            font-weight:600;margin:0.8rem 0 0.4rem;font-family:'Inter',sans-serif;">
  Writing Tone
</div>
""", unsafe_allow_html=True)
        tones = {
            "professional": "💼 Professional",
            "enthusiastic": "🔥 Enthusiastic",
            "concise": "⚡ Concise",
            "storytelling": "📖 Storytelling",
        }
        tone = st.radio("Tone", list(tones.values()), horizontal=True,
                        label_visibility="collapsed", key="cl_tone")
        tone_key = [k for k, v in tones.items() if v == tone][0]

        if st.button("✨ Generate Cover Letter", use_container_width=True):
            with st.spinner("Crafting your cover letter..."):
                r = api("POST", "/coverletter/generate", timeout=600, json={
                    "resume_id": resume_opts[sel_r],
                    "job_id": job_opts[sel_j],
                    "tone": tone_key,
                })
            if r and r.ok:
                st.session_state["cl_result"] = r.json()
            elif r:
                detail = ""
                try:
                    detail = r.json().get("detail", "")
                except Exception:
                    detail = f"HTTP {r.status_code}"
                if r.status_code in (429, 503) or "quota" in detail.lower() or "api key" in detail.lower():
                    st.error(
                        "🔑 **API Key Issue** — Your API key quota may be exhausted. "
                        "Go to **Settings** to check your API key."
                    )
                else:
                    st.error(detail or "Generation failed.")

        result = st.session_state.get("cl_result")
        if result:
            letter = result.get("cover_letter") or result.get("letter") or result.get("content", "")
            if letter:
                st.markdown("---")
                st.markdown(f"""
<div style="background:rgba(19,19,43,0.6);border:1px solid rgba(139,92,246,0.12);
            border-radius:14px;padding:1.5rem 1.8rem;margin:0.5rem 0;
            backdrop-filter:blur(10px);font-family:'Inter',sans-serif;
            font-size:0.88rem;line-height:1.7;color:#D0D0E8;
            border-left:3px solid #8B5CF6;animation:fadeInUp 0.5s ease;">
  {letter.replace(chr(10), '<br>')}
</div>
""", unsafe_allow_html=True)
                st.download_button(
                    "📥 Download as Text",
                    letter,
                    file_name="cover_letter.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

    with tab_saved:
        r = api("GET", "/coverletter/")
        if not r or not r.ok:
            st.error("Failed to load saved letters.")
            return
        letters = r.json()
        if not letters:
            render_empty_state(None, "No saved letters", "Generate your first cover letter above.")
            return

        for cl in letters:
            tone_badge = cl.get("tone", "professional")
            tone_icon = {"professional": "💼", "enthusiastic": "🔥",
                         "concise": "⚡", "storytelling": "📖"}.get(tone_badge, "📝")

            with st.expander(f"{tone_icon} Cover Letter #{cl['id']}"):
                content = cl.get("cover_letter") or cl.get("letter") or cl.get("content", "")
                if content:
                    st.markdown(f"""
<div style="font-size:0.85rem;color:#B0B0CC;line-height:1.7;font-family:'Inter',sans-serif;">
  {content[:600]}{'...' if len(content) > 600 else ''}
</div>
""", unsafe_allow_html=True)
                if st.button("🗑 Delete", key=f"del_cl_{cl['id']}"):
                    dr = api("DELETE", f"/coverletter/{cl['id']}")
                    if dr and dr.ok:
                        st.rerun()
