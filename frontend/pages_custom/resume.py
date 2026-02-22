import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state
import json


def render():
    render_page_header("Resume Manager", "Upload and manage your resumes")

    tab_upload, tab_list = st.tabs(["Upload New", "My Resumes"])

    with tab_upload:
        st.markdown("<br>", unsafe_allow_html=True)
        file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
        st.markdown('<p class="upload-hint">Supports PDF, DOCX, and TXT formats</p>', unsafe_allow_html=True)
        if file:
            if st.button("⬆️ Upload & Parse Resume", use_container_width=True):
                with st.spinner("Parsing your resume with AI…"):
                    r = api("POST", "/resume/upload", files={"file": (file.name, file.getvalue(), file.type)})
                if r and r.ok:
                    st.success("✅ Resume uploaded and parsed.")
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Upload failed."))

    with tab_list:
        st.markdown("<br>", unsafe_allow_html=True)
        r = api("GET", "/resume/")
        if not r or not r.ok:
            st.error("Failed to load resumes.")
            return
        resumes = r.json()
        if not resumes:
            render_empty_state("📄", "No resumes yet", "Upload your first resume using the tab above.")
            return

        for res in resumes:
            with st.expander(f"📄 {res.get('original_filename', 'Resume')} — uploaded {str(res.get('created_at',''))[:10]}"):
                parsed = res.get("parsed_json", {})
                if not parsed:
                    st.info("No parsed data available.")
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Name:** {parsed.get('name','—')}")
                        st.markdown(f"**Email:** {parsed.get('email','—')}")
                        st.markdown(f"**Phone:** {parsed.get('phone','—')}")
                    with c2:
                        st.markdown(f"**Title:** {parsed.get('current_title','') or parsed.get('title','—')}")
                        st.markdown(f"**Location:** {parsed.get('location','—')}")

                    skills = parsed.get("skills", {})
                    if skills:
                        st.markdown("**Skills**")
                        if isinstance(skills, dict):
                            for cat, skill_list in skills.items():
                                if skill_list:
                                    pills = "".join(f'<span class="badge badge-skill">{s}</span>' for s in skill_list)
                                    st.markdown(f"<div style='margin-bottom:4px'><span style='color:#6b7280;font-size:0.8rem'>{cat}: </span>{pills}</div>", unsafe_allow_html=True)
                        elif isinstance(skills, list):
                            pills = "".join(f'<span class="badge badge-skill">{s}</span>' for s in skills)
                            st.markdown(f"<div>{pills}</div>", unsafe_allow_html=True)

                    if parsed.get("summary"):
                        with st.expander("Summary"):
                            st.write(parsed["summary"])

                if st.button(f"🗑️ Delete", key=f"del_res_{res['id']}"):
                    dr = api("DELETE", f"/resume/{res['id']}")
                    if dr and dr.ok:
                        st.success("Deleted.")
                        st.rerun()
