import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


@st.cache_data(ttl=60, show_spinner=False)
def fetch_jobs(token):
    from utils.auth import api
    r = api("GET", "/jobs/")
    if r and r.ok:
        return r.json()
    return None


def render():
    render_page_header("Job Analyzer", "Paste or link a job description to analyze it with AI")

    tab_add, tab_list = st.tabs(["Add New Job", "My Jobs"])

    with tab_add:
        input_mode = st.radio("Input method", ["Paste text", "From URL"], horizontal=True)

        raw_text = ""
        source_url = None

        if input_mode == "Paste text":
            raw_text = st.text_area("Job description", height=220, placeholder="Paste the full job description here")
        else:
            source_url = st.text_input("Job posting URL")

        col_a, col_b = st.columns(2)
        with col_a:
            company = st.text_input("Company name (optional)")
        with col_b:
            title = st.text_input("Job title (optional)")

        if st.button("Analyze Job", use_container_width=True):
            if not raw_text.strip() and not source_url:
                st.error("Provide a job description or URL.")
            else:
                with st.spinner("Analyzing..."):
                    r = api("POST", "/jobs/parse", json={
                        "raw_text": raw_text,
                        "source_url": source_url,
                        "company_name": company,
                        "job_title": title
                    })
                if r and r.ok:
                    st.success("Job analyzed and saved.")
                    fetch_jobs.clear()
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Analysis failed."))

    with tab_list:
        token = st.session_state.get("token")
        jobs = fetch_jobs(token)
        if jobs is None:
            st.error("Failed to load jobs.")
            return

        if not jobs:
            render_empty_state(None, "No jobs yet", "Analyze your first job description above.")
            return

        for job in jobs:
            parsed = job.get("parsed_json", {}) or {}
            title_label = job.get("job_title") or parsed.get("job_title", "Untitled Job")
            company_label = job.get("company_name") or parsed.get("company", "Unknown Company")
            date = str(job.get("created_at", ""))[:10]

            with st.expander(f"{title_label} @ {company_label}  |  {date}"):
                c1, c2 = st.columns(2)
                with c1:
                    if parsed.get("required_skills"):
                        st.markdown("**Required Skills**")
                        st.write(", ".join(parsed["required_skills"]))
                with c2:
                    if parsed.get("preferred_skills"):
                        st.markdown("**Preferred Skills**")
                        st.write(", ".join(parsed["preferred_skills"]))

                for field, label in [("experience_required", "Experience"), ("location", "Location"), ("employment_type", "Type")]:
                    val = parsed.get(field)
                    if val:
                        st.markdown(f"**{label}:** {val}")

                if st.button("Delete", key=f"del_job_{job['id']}"):
                    dr = api("DELETE", f"/jobs/{job['id']}")
                    if dr and dr.ok:
                        st.success("Deleted.")
                        fetch_jobs.clear()
                        st.rerun()
