import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


@st.cache_data(ttl=60, show_spinner=False)
def fetch_resumes(token):
    from utils.auth import api
    r = api("GET", "/resume/")
    if r and r.ok:
        return r.json()
    return None


def render():
    render_page_header("Resume Manager", "Upload and manage your resumes")

    tab_upload, tab_list = st.tabs(["Upload New", "My Resumes"])

    with tab_upload:
        file = st.file_uploader("Upload your resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if file:
            if st.button("Upload and Parse", use_container_width=True):
                with st.spinner("Parsing resume..."):
                    r = api("POST", "/resume/upload", files={"file": (file.name, file.getvalue(), file.type)})
                if r and r.ok:
                    st.success("Resume uploaded and parsed.")
                    fetch_resumes.clear()
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Upload failed."))

    with tab_list:
        token = st.session_state.get("token")
        resumes = fetch_resumes(token)
        if resumes is None:
            st.error("Failed to load resumes.")
            return

        if not resumes:
            render_empty_state(None, "No resumes yet", "Upload your first resume using the tab above.")
            return

        for res in resumes:
            with st.expander(f"{res.get('original_filename', 'Resume')} — {str(res.get('created_at', ''))[:10]}"):
                parsed = res.get("parsed_json", {})
                if not parsed:
                    st.info("No parsed data available.")
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Name:** {parsed.get('name', '—')}")
                        st.markdown(f"**Email:** {parsed.get('email', '—')}")
                        st.markdown(f"**Phone:** {parsed.get('phone', '—')}")
                    with c2:
                        st.markdown(f"**Title:** {parsed.get('current_title', '') or parsed.get('title', '—')}")
                        st.markdown(f"**Location:** {parsed.get('location', '—')}")

                    skills = parsed.get("skills", {})
                    if skills:
                        st.markdown("**Skills**")
                        if isinstance(skills, dict):
                            for cat, skill_list in skills.items():
                                if skill_list:
                                    st.markdown(f"_{cat}:_ {', '.join(skill_list)}")
                        elif isinstance(skills, list):
                            st.markdown(", ".join(skills))

                    if parsed.get("summary"):
                        with st.expander("Summary"):
                            st.write(parsed["summary"])

                if st.button("Delete", key=f"del_res_{res['id']}"):
                    dr = api("DELETE", f"/resume/{res['id']}")
                    if dr and dr.ok:
                        st.success("Deleted.")
                        fetch_resumes.clear()
                        st.rerun()
