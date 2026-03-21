import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


def render():
    render_page_header("Jobs Manager", "Track job descriptions for matching and analysis")

    tab_add, tab_list = st.tabs(["Add Job", "My Jobs"])

    with tab_add:
        st.markdown("""
<div style="font-size:0.85rem;color:#8B8BA8;font-family:'Inter',sans-serif;margin-bottom:0.8rem;">
  Paste a full job description or enter details manually
</div>
""", unsafe_allow_html=True)

        mode = st.radio("Input mode", ["Paste Full Description", "Manual Entry"],
                        horizontal=True, label_visibility="collapsed")

        if mode == "Paste Full Description":
            raw = st.text_area("Job description", height=200,
                               placeholder="Paste the complete job description here...")
            if st.button("⚡ Parse & Save", use_container_width=True):
                if not raw.strip():
                    st.error("Please paste a job description.")
                else:
                    with st.spinner("Parsing job description with AI..."):
                        r = api("POST", "/jobs/parse", timeout=600, json={"raw_text": raw})
                    if r and r.ok:
                        st.success("✅ Job parsed and saved!")
                        st.rerun()
                    elif r:
                        st.error(r.json().get("detail", "Parse failed."))
        else:
            with st.form("job_form"):
                c1, c2 = st.columns(2)
                with c1:
                    title = st.text_input("Job Title", placeholder="e.g. ML Engineer")
                with c2:
                    company = st.text_input("Company", placeholder="e.g. Google")
                description = st.text_area("Description", height=120,
                                           placeholder="Key responsibilities and requirements...")
                c3, c4 = st.columns(2)
                with c3:
                    req_skills = st.text_input("Required Skills (comma separated)",
                                               placeholder="Python, TensorFlow, SQL")
                with c4:
                    pref_skills = st.text_input("Preferred Skills (comma separated)",
                                                placeholder="Kubernetes, Spark")
                submitted = st.form_submit_button("Save Job", use_container_width=True)
                if submitted:
                    if not title:
                        st.error("Job title is required.")
                    else:
                        r = api("POST", "/jobs/", json={
                            "job_title": title,
                            "company_name": company,
                            "description": description,
                            "required_skills": [s.strip() for s in req_skills.split(",") if s.strip()],
                            "preferred_skills": [s.strip() for s in pref_skills.split(",") if s.strip()],
                        })
                        if r and r.ok:
                            st.success("✅ Job saved!")
                            st.rerun()
                        elif r:
                            st.error(r.json().get("detail", "Save failed."))

    with tab_list:
        r = api("GET", "/jobs/")
        if not r or not r.ok:
            st.error("Failed to load jobs.")
            return
        jobs = r.json()
        if not jobs:
            render_empty_state(None, "No jobs tracked", "Add your first job in the Add Job tab.")
            return

        for j in jobs:
            title = j.get("job_title", "Untitled")
            company = j.get("company_name", "")
            header = f"💼 {title}"
            if company:
                header += f" @ {company}"

            with st.expander(header):
                if j.get("description"):
                    st.markdown(f"""
<div style="font-size:0.83rem;color:#B0B0CC;line-height:1.6;font-family:'Inter',sans-serif;
            max-height:180px;overflow-y:auto;padding-right:0.5rem;">
  {j['description'][:500]}{'...' if len(j.get('description', '')) > 500 else ''}
</div>
""", unsafe_allow_html=True)

                # ── Skills ──
                req = j.get("required_skills") or []
                pref = j.get("preferred_skills") or []

                if req or pref:
                    badges_html = ""
                    for sk in req:
                        badges_html += (
                            f'<span style="display:inline-block;padding:0.18rem 0.6rem;'
                            f'border-radius:16px;font-size:0.72rem;font-weight:600;'
                            f'background:rgba(139,92,246,0.12);color:#C4B5FD;'
                            f'border:1px solid rgba(139,92,246,0.25);margin:2px;'
                            f'font-family:\'Inter\',sans-serif;">{sk}</span>'
                        )
                    for sk in pref:
                        badges_html += (
                            f'<span style="display:inline-block;padding:0.18rem 0.6rem;'
                            f'border-radius:16px;font-size:0.72rem;font-weight:500;'
                            f'background:rgba(75,85,99,0.15);color:#9CA3AF;'
                            f'border:1px solid rgba(75,85,99,0.25);margin:2px;'
                            f'font-family:\'Inter\',sans-serif;">{sk}</span>'
                        )
                    st.markdown(f"""
<div style="margin-top:0.6rem;">
  <div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
              font-weight:600;margin-bottom:0.3rem;font-family:'Inter',sans-serif;">Skills Required</div>
  {badges_html}
</div>
""", unsafe_allow_html=True)

                st.markdown('<div style="height:0.3rem;"></div>', unsafe_allow_html=True)
                if st.button("🗑 Delete Job", key=f"del_job_{j['id']}", use_container_width=True):
                    dr = api("DELETE", f"/jobs/{j['id']}")
                    if dr and dr.ok:
                        st.rerun()
