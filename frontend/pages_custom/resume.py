import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


def render():
    render_page_header("Resume Manager", "Upload, parse, and manage your resumes")

    tab_upload, tab_list = st.tabs(["Upload", "My Resumes"])

    with tab_upload:
        st.markdown("""
<div style="text-align:center;padding:1.2rem 0 0.5rem;color:#8B8BA8;font-size:0.85rem;
            font-family:'Inter',sans-serif;">
  Upload a PDF or DOCX resume — our AI will parse it instantly
</div>
""", unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Drop your resume here",
            type=["pdf", "docx"],
            label_visibility="collapsed",
        )
        if uploaded:
            if st.button("⚡ Upload & Parse", use_container_width=True):
                with st.spinner("Parsing your resume with AI..."):
                    r = api("POST", "/resume/upload", timeout=600,
                            files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)})
                if r and r.ok:
                    st.success("✅ Resume uploaded and parsed successfully!")
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Upload failed."))

    with tab_list:
        r = api("GET", "/resume/")
        if not r or not r.ok:
            st.error("Failed to load resumes.")
            return
        resumes = r.json()
        if not resumes:
            render_empty_state(None, "No resumes uploaded", "Upload your first resume in the Upload tab above.")
            return

        for res in resumes:
            title = res.get("original_filename", f"Resume #{res['id']}")
            parsed = res.get("parsed_json") or {}
            name = parsed.get("name", "")
            current_title = parsed.get("current_title", "") or parsed.get("title", "")

            with st.expander(f"📄 {title}"):
                # ── Header Info ──
                if name or current_title:
                    st.markdown(f"""
<div style="background:rgba(19,19,43,0.5);border:1px solid rgba(139,92,246,0.1);
            border-radius:10px;padding:0.8rem 1rem;margin-bottom:0.8rem;">
  <div style="font-size:0.95rem;font-weight:700;color:#E8E8F0;font-family:'Inter',sans-serif;">
    {name or '—'}
  </div>
  <div style="font-size:0.8rem;color:#8B8BA8;font-family:'Inter',sans-serif;margin-top:0.1rem;">
    {current_title or '—'}
  </div>
</div>
""", unsafe_allow_html=True)

                # ── Skills ──
                skills_all = parsed.get("skills", {})
                if skills_all:
                    all_skills = []
                    if isinstance(skills_all, dict):
                        for cat, s_list in skills_all.items():
                            all_skills.extend(s_list or [])
                    elif isinstance(skills_all, list):
                        all_skills = skills_all

                    if all_skills:
                        badges = ""
                        for sk in all_skills[:12]:
                            badges += (
                                f'<span style="display:inline-block;padding:0.18rem 0.6rem;'
                                f'border-radius:16px;font-size:0.72rem;font-weight:600;'
                                f'background:rgba(99,102,241,0.12);color:#A5B4FC;'
                                f'border:1px solid rgba(99,102,241,0.25);margin:2px;'
                                f'font-family:\'Inter\',sans-serif;">{sk}</span>'
                            )
                        if len(all_skills) > 12:
                            badges += (
                                f'<span style="display:inline-block;padding:0.18rem 0.6rem;'
                                f'border-radius:16px;font-size:0.72rem;font-weight:500;'
                                f'color:#6B6B8D;font-family:\'Inter\',sans-serif;">'
                                f'+{len(all_skills) - 12} more</span>'
                            )
                        st.markdown(f"""
<div style="margin-bottom:0.5rem;">
  <div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
              font-weight:600;margin-bottom:0.3rem;font-family:'Inter',sans-serif;">Skills</div>
  {badges}
</div>
""", unsafe_allow_html=True)

                # ── Education ──
                education = parsed.get("education", [])
                if education:
                    for edu in education[:2]:
                        if isinstance(edu, dict):
                            st.markdown(
                                f"🎓 **{edu.get('degree', '')}** — {edu.get('institution', '')} "
                                f"({edu.get('year', '')})"
                            )
                        else:
                            st.markdown(f"🎓 {edu}")

                # ── Delete ──
                st.markdown('<div style="height:0.3rem;"></div>', unsafe_allow_html=True)
                if st.button("🗑 Delete Resume", key=f"del_res_{res['id']}",
                             use_container_width=True):
                    dr = api("DELETE", f"/resume/{res['id']}")
                    if dr and dr.ok:
                        st.rerun()
