import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


def render():
    render_page_header("Job Analyzer", "Paste or link a job description to analyze it with AI")

    tab_add, tab_list = st.tabs(["Add New Job", "My Jobs"])

    with tab_add:
        st.markdown("<br>", unsafe_allow_html=True)
        input_mode = st.radio("Input method", ["Paste text", "From URL"], horizontal=True)

        raw_text = ""
        source_url = None

        if input_mode == "Paste text":
            raw_text = st.text_area("Job description", height=220, placeholder="Paste the full job description here…")
        else:
            source_url = st.text_input("Job posting URL", placeholder="https://jobs.example.com/software-engineer")

        col_a, col_b = st.columns(2)
        with col_a:
            company = st.text_input("Company name (optional)")
        with col_b:
            title = st.text_input("Job title (optional)")

        if st.button("🔍 Analyze Job", use_container_width=True):
            if not raw_text.strip() and not source_url:
                st.error("Provide a job description or URL.")
            else:
                with st.spinner("Analyzing with AI…"):
                    r = api("POST", "/jobs/parse", json={
                        "raw_text": raw_text,
                        "source_url": source_url,
                        "company_name": company,
                        "job_title": title
                    })
                if r and r.ok:
                    st.success("✅ Job analyzed and saved.")
                    st.session_state["last_job"] = r.json()
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Analysis failed."))

    with tab_list:
        st.markdown("<br>", unsafe_allow_html=True)
        r = api("GET", "/jobs/")
        if not r or not r.ok:
            st.error("Failed to load jobs.")
            return
        jobs = r.json()
        if not jobs:
            render_empty_state("💼", "No jobs yet", "Analyze your first job description above.")
            return

        for job in jobs:
            parsed = job.get("parsed_json", {}) or {}
            title_label = job.get("job_title") or parsed.get("job_title", "Untitled Job")
            company_label = job.get("company_name") or parsed.get("company", "Unknown Company")
            date = str(job.get("created_at", ""))[:10]

            with st.expander(f"💼 {title_label} @ {company_label}  ·  {date}"):
                c1, c2 = st.columns(2)
                with c1:
                    if parsed.get("required_skills"):
                        st.markdown("**Required Skills**")
                        pills = "".join(f'<span class="badge badge-skill">{s}</span>' for s in parsed["required_skills"])
                        st.markdown(f"<div style='margin-bottom:0.6rem'>{pills}</div>", unsafe_allow_html=True)
                with c2:
                    if parsed.get("preferred_skills"):
                        st.markdown("**Preferred Skills**")
                        pills = "".join(f'<span class="badge badge-matched">{s}</span>' for s in parsed["preferred_skills"])
                        st.markdown(f"<div style='margin-bottom:0.6rem'>{pills}</div>", unsafe_allow_html=True)

                for field, label in [("experience_required", "Experience"), ("location", "Location"), ("employment_type", "Type")]:
                    val = parsed.get(field)
                    if val:
                        st.markdown(f"**{label}:** {val}")

                if st.button(f"🗑️ Delete", key=f"del_job_{job['id']}"):
                    dr = api("DELETE", f"/jobs/{job['id']}")
                    if dr and dr.ok:
                        st.success("Deleted.")
                        st.rerun()
