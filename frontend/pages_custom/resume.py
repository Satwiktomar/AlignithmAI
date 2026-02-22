import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state
import json



SVG_TARGET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>"""
SVG_DOC = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
SVG_CHAT = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>"""
SVG_BUILDING = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>"""
SVG_ROCKET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 2.18 0 0 0-2.91-.09z"></path><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path></svg>"""
SVG_WIFI = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>"""

def render():
    render_page_header("Resume Manager", "Upload and manage your resumes")

    tab_upload, tab_list = st.tabs(["Upload New", "My Resumes"])

    with tab_upload:
        st.markdown("<br>", unsafe_allow_html=True)
        file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
        st.markdown('<p class="upload-hint">Supports PDF, DOCX, and TXT formats</p>', unsafe_allow_html=True)
        if file:
            if st.button("Upload & Parse Resume", use_container_width=True):
                with st.spinner("Parsing your resume with AI…"):
                    r = api("POST", "/resume/upload", files={"file": (file.name, file.getvalue(), file.type)})
                if r and r.ok:
                    st.success("Resume uploaded and parsed.")
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
            render_empty_state(SVG_DOC, "No resumes yet", "Upload your first resume using the tab above.")
            return

        for res in resumes:
            with st.expander(f"{res.get('original_filename', 'Resume')} — uploaded {str(res.get('created_at',''))[:10]}"):
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

                if st.button(f"Delete", key=f"del_res_{res['id']}"):
                    dr = api("DELETE", f"/resume/{res['id']}")
                    if dr and dr.ok:
                        st.success("Deleted.")
                        st.rerun()
