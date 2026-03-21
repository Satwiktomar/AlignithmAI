import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


def render():
    render_page_header("Version Manager", "Save and compare resume snapshots")

    tab_save, tab_list = st.tabs(["Save Version", "My Versions"])

    with tab_save:
        r_res = api("GET", "/resume/")
        if not r_res or not r_res.ok:
            st.error("Failed to load resumes.")
            return
        resumes = r_res.json()
        if not resumes:
            render_empty_state(None, "No resumes", "Upload a resume first.")
            return

        resume_opts = {f"{r.get('original_filename', 'Resume')} (#{r['id']})": r["id"] for r in resumes}
        sel_r = st.selectbox("Resume to snapshot", list(resume_opts.keys()), key="ver_resume")

        label = st.text_input("Version label", placeholder="e.g. v2 – added ML projects")

        if st.button("📋 Save Snapshot", use_container_width=True):
            if not label.strip():
                st.error("Enter a version label.")
            else:
                with st.spinner("Saving version snapshot..."):
                    r = api("POST", "/versions/", timeout=600, json={
                        "resume_id": resume_opts[sel_r],
                        "label": label.strip(),
                    })
                if r and r.ok:
                    st.success("✅ Version saved!")
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Save failed."))

    with tab_list:
        r = api("GET", "/versions/")
        if not r or not r.ok:
            st.error("Failed to load versions.")
            return
        versions = r.json()
        if not versions:
            render_empty_state(None, "No versions saved", "Save your first version above.")
            return

        for v in versions:
            label = v.get("label", f"Version #{v['id']}")
            created = v.get("created_at", "")
            if created and "T" in str(created):
                created = str(created).split("T")[0]

            with st.expander(f"📋 {label} · {created}"):
                data = v.get("snapshot") or v.get("data") or {}

                if isinstance(data, dict):
                    name = data.get("name", "")
                    title = data.get("current_title", "") or data.get("title", "")
                    if name or title:
                        st.markdown(f"""
<div style="background:rgba(19,19,43,0.5);border:1px solid rgba(139,92,246,0.1);
            border-radius:10px;padding:0.6rem 0.8rem;margin-bottom:0.6rem;">
  <div style="font-size:0.9rem;font-weight:600;color:#E8E8F0;font-family:'Inter',sans-serif;">
    {name or '—'}
  </div>
  <div style="font-size:0.78rem;color:#8B8BA8;font-family:'Inter',sans-serif;">{title or '—'}</div>
</div>
""", unsafe_allow_html=True)

                    skills = data.get("skills", {})
                    all_skills = []
                    if isinstance(skills, dict):
                        for cat, sl in skills.items():
                            all_skills.extend(sl or [])
                    elif isinstance(skills, list):
                        all_skills = skills

                    if all_skills:
                        badges = ""
                        for sk in all_skills[:10]:
                            badges += (
                                f'<span style="display:inline-block;padding:0.18rem 0.55rem;'
                                f'border-radius:16px;font-size:0.7rem;font-weight:600;'
                                f'background:rgba(99,102,241,0.12);color:#A5B4FC;'
                                f'border:1px solid rgba(99,102,241,0.25);margin:2px;'
                                f'font-family:\'Inter\',sans-serif;">{sk}</span>'
                            )
                        st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.json(data)

                if st.button("🗑 Delete Version", key=f"del_ver_{v['id']}"):
                    dr = api("DELETE", f"/versions/{v['id']}")
                    if dr and dr.ok:
                        st.rerun()
