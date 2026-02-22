import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state



SVG_TARGET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>"""
SVG_DOC = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
SVG_CHAT = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>"""
SVG_BUILDING = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>"""
SVG_ROCKET = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 2.18 0 0 0-2.91-.09z"></path><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path></svg>"""
SVG_WIFI = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>"""

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

        if st.button("Analyze Job", use_container_width=True):
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
                    st.success("Job analyzed and saved.")
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
            render_empty_state(SVG_BUILDING, "No jobs yet", "Analyze your first job description above.")
            return

        for job in jobs:
            parsed = job.get("parsed_json", {}) or {}
            title_label = job.get("job_title") or parsed.get("job_title", "Untitled Job")
            company_label = job.get("company_name") or parsed.get("company", "Unknown Company")
            date = str(job.get("created_at", ""))[:10]

            with st.expander(f"{title_label} @ {company_label}  ·  {date}"):
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

                if st.button(f"Delete", key=f"del_job_{job['id']}"):
                    dr = api("DELETE", f"/jobs/{job['id']}")
                    if dr and dr.ok:
                        st.success("Deleted.")
                        st.rerun()
