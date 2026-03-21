import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_stat_card, score_color


def render():
    render_page_header("Dashboard", "Your career intelligence at a glance")

    r_res = api("GET", "/resume/")
    r_jobs = api("GET", "/jobs/")
    r_proj = api("GET", "/projects/")
    r_cl = api("GET", "/coverletter/")

    resumes = r_res.json() if r_res and r_res.ok else []
    jobs = r_jobs.json() if r_jobs and r_jobs.ok else []
    projects = r_proj.json() if r_proj and r_proj.ok else []
    letters = r_cl.json() if r_cl and r_cl.ok else []

    # ── Stat Cards ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card(len(resumes), "Resumes", "📄")
    with c2:
        render_stat_card(len(jobs), "Jobs Tracked", "💼")
    with c3:
        render_stat_card(len(projects), "Projects", "🚀")
    with c4:
        render_stat_card(len(letters), "Cover Letters", "✉️")

    st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

    # ── Recent Match Scores ──
    if resumes and jobs:
        st.markdown("""
<div style="font-size:0.8rem;color:#8B8BA8;text-transform:uppercase;letter-spacing:0.08em;
            font-weight:600;font-family:'Inter',sans-serif;margin-bottom:0.6rem;">
  Recent Match Scores
</div>
""", unsafe_allow_html=True)

        r_scores = api("GET", "/match/")
        if r_scores and r_scores.ok:
            scores = r_scores.json()
            if scores:
                for s in scores[:6]:
                    score = int(float(s.get("overall_score", s.get("score", 0))))
                    color = score_color(score)

                    res_name = ""
                    job_label = ""
                    for re in resumes:
                        if re["id"] == s.get("resume_id"):
                            res_name = re.get("original_filename", f"Resume #{re['id']}")
                    for j in jobs:
                        if j["id"] == s.get("job_id"):
                            job_label = f"{j.get('job_title', '')} @ {j.get('company_name', '')}"

                    st.markdown(f"""
<div style="background:rgba(19,19,43,0.5);border:1px solid rgba(139,92,246,0.1);
            border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.4rem;
            display:flex;align-items:center;justify-content:space-between;
            backdrop-filter:blur(6px);transition:all 0.2s ease;
            animation:fadeInUp 0.4s ease;"
     onmouseover="this.style.borderColor='rgba(139,92,246,0.25)'"
     onmouseout="this.style.borderColor='rgba(139,92,246,0.1)'">
  <div style="flex:1;">
    <div style="font-size:0.85rem;font-weight:600;color:#E8E8F0;font-family:'Inter',sans-serif;">
      {res_name}
    </div>
    <div style="font-size:0.75rem;color:#8B8BA8;font-family:'Inter',sans-serif;">
      {job_label}
    </div>
  </div>
  <div style="background:{color}18;border:1px solid {color}40;border-radius:8px;
              padding:0.3rem 0.7rem;font-size:0.9rem;font-weight:700;color:{color};
              font-family:'Inter',sans-serif;min-width:48px;text-align:center;">
    {score}
  </div>
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown("""
<div style="text-align:center;padding:1.5rem;color:#6B6B8D;font-family:'Inter',sans-serif;
            background:rgba(19,19,43,0.3);border-radius:12px;border:1px dashed rgba(139,92,246,0.15);">
  No match scores yet. Go to <strong>Match Report</strong> to analyze your resume-job fit.
</div>
""", unsafe_allow_html=True)
    else:
        # ── Welcome State ──
        st.markdown("""
<div style="text-align:center;padding:3rem 1.5rem;
            background:linear-gradient(135deg,rgba(19,19,43,0.7) 0%,rgba(99,102,241,0.05) 100%);
            border-radius:16px;border:1px solid rgba(139,92,246,0.12);
            backdrop-filter:blur(12px);animation:fadeInUp 0.5s ease;">
  <div style="font-size:1.8rem;margin-bottom:0.5rem;">🎯</div>
  <div style="font-size:1.1rem;font-weight:700;color:#E8E8F0;margin-bottom:0.3rem;
              font-family:'Inter',sans-serif;">
    Welcome to Alignithm.AI
  </div>
  <div style="font-size:0.85rem;color:#8B8BA8;line-height:1.6;max-width:400px;
              margin:0 auto;font-family:'Inter',sans-serif;">
    Start by uploading a <strong>Resume</strong> and adding a <strong>Job Description</strong>
    to unlock AI-powered matching, cover letter generation, skill gap analysis, and more.
  </div>
</div>
""", unsafe_allow_html=True)
