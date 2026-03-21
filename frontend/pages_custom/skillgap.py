import json
import streamlit as st
import streamlit.components.v1 as components
from utils.auth import api
from utils.styles import render_page_header, render_empty_state


# ---------------------------------------------------------------------------
# Roadmap.sh-style elaborate flowchart with prerequisite branching
# ---------------------------------------------------------------------------

def _build_roadmap_flowchart(
    steps: list[dict],
    matched_skills: list[str] = None,
    missing_skills: list[str] = None,
) -> str:
    """
    Build a roadmap.sh-style flowchart with prerequisite dependency trees.

    Colour coding:
      Green  (#22c55e) = Must-learn (critical / high priority)
      Yellow (#fef08a) = Should-learn (medium priority)
      White  (#ffffff) = Nice to know (low priority)
      Light-green (#bbf7d0) = Already known
    """
    matched_set = set(s.lower().strip() for s in (matched_skills or []))

    nodes = []
    for i, step in enumerate(steps[:12]):
        if isinstance(step, dict):
            skill = step.get("skill", f"Step {i+1}")
            action = step.get("action") or step.get("resource", "")
            why = step.get("why_needed", "")
            timeline = step.get("timeline", "")
            hours = step.get("estimated_hours", "")
            priority = (step.get("priority") or "medium").lower()
            category = step.get("category", "")
            proficiency = step.get("proficiency_target", "")
            prereqs = step.get("prerequisites") or []
            resources = step.get("resources") or []
        else:
            skill = str(step)
            action, why, timeline, hours = "", "", "", ""
            priority, category, proficiency = "medium", "", ""
            prereqs, resources = [], []

        # Colour by priority
        if priority in ("critical", "high"):
            color, border, text_color = "#22c55e", "#16a34a", "#052e16"
        elif priority == "medium":
            color, border, text_color = "#fef08a", "#eab308", "#422006"
        else:
            color, border, text_color = "#ffffff", "#d1d5db", "#1f2937"

        # Process prerequisites
        prereq_list = []
        for pr in prereqs[:4]:
            if isinstance(pr, dict):
                pr_name = pr.get("name", "")
                pr_desc = pr.get("description", "")
                pr_known = pr.get("already_known", False) or (pr_name.lower().strip() in matched_set)
                prereq_list.append({"name": pr_name, "desc": pr_desc, "known": pr_known})
            elif isinstance(pr, str):
                pr_known = pr.lower().strip() in matched_set
                prereq_list.append({"name": pr, "desc": "", "known": pr_known})

        # Process resources
        res_list = []
        for rs in resources[:3]:
            if isinstance(rs, dict):
                res_list.append({
                    "title": rs.get("title", ""),
                    "url": rs.get("url", ""),
                    "type": rs.get("type", ""),
                })
            elif isinstance(rs, str):
                res_list.append({"title": rs, "url": "", "type": ""})

        nodes.append({
            "skill": skill,
            "action": action[:100],
            "why": why[:100],
            "timeline": timeline,
            "hours": str(hours) if hours else "",
            "color": color,
            "border": border,
            "textColor": text_color,
            "priority": priority,
            "category": category,
            "proficiency": proficiency,
            "prereqs": prereq_list,
            "resources": res_list,
        })

    nodes_json = json.dumps(nodes)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #0f172a;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    color: #e2e8f0;
    padding: 16px 8px;
  }}
  .fc-title {{ text-align: center; font-size: 18px; font-weight: 700; color: #f1f5f9;
               margin-bottom: 16px; letter-spacing: 0.3px; }}
  .flowchart {{ display: flex; flex-direction: column; align-items: center; gap: 0; }}

  /* ── Main skill node ── */
  .skill-group {{ width: 92%; max-width: 600px; }}

  .node-box {{
    position: relative;
    padding: 14px 18px 12px;
    border-radius: 10px;
    border-left: 5px solid;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    transition: transform 0.15s, box-shadow 0.15s;
  }}
  .node-box:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.4); }}

  .node-num {{
    position: absolute; top: -10px; left: -10px;
    width: 26px; height: 26px; border-radius: 50%;
    background: #1e293b; border: 2px solid #475569;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: #94a3b8;
  }}
  .node-header {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; }}
  .node-skill {{ font-size: 14px; font-weight: 700; }}
  .node-badges {{ display: flex; gap: 4px; flex-wrap: wrap; }}
  .badge {{
    font-size: 9px; padding: 2px 6px; border-radius: 9px;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px;
    white-space: nowrap;
  }}
  .badge-cat {{ background: rgba(0,0,0,0.12); }}
  .badge-prof {{ background: rgba(0,0,0,0.08); }}
  .node-action {{ font-size: 11.5px; opacity: 0.85; line-height: 1.4; margin-top: 4px; }}
  .node-why {{ font-size: 10.5px; opacity: 0.65; font-style: italic; margin-top: 3px; }}

  .node-meta {{ font-size: 10.5px; margin-top: 6px; opacity: 0.7;
                 display: flex; gap: 12px; flex-wrap: wrap; }}

  .node-resources {{ margin-top: 6px; padding-top: 5px; border-top: 1px solid rgba(0,0,0,0.1); }}
  .node-resources-title {{ font-size: 10px; font-weight: 700; opacity: 0.6; margin-bottom: 3px; }}
  .res-link {{
    font-size: 10.5px; color: inherit; text-decoration: underline;
    opacity: 0.8; display: inline-block; margin-right: 10px;
  }}
  .res-tag {{ font-size: 8px; opacity: 0.5; margin-left: 2px; }}

  /* ── Prereq branch ── */
  .prereq-row {{
    display: flex; align-items: center; justify-content: center;
    gap: 8px; flex-wrap: wrap;
    margin: 4px 0 0; padding-left: 28px;
  }}
  .prereq-box {{
    font-size: 10.5px; padding: 5px 10px; border-radius: 6px;
    border: 1.5px solid; position: relative; max-width: 190px;
    line-height: 1.3;
  }}
  .prereq-known {{ background: #bbf7d0; border-color: #22c55e; color: #052e16; }}
  .prereq-needed {{ background: #1e293b; border-color: #475569; color: #cbd5e1; }}
  .prereq-name {{ font-weight: 600; }}
  .prereq-desc {{ font-size: 9px; opacity: 0.7; }}
  .prereq-check {{ font-size: 10px; }}

  .prereq-connector {{
    display: flex; flex-direction: column; align-items: center; height: 16px;
  }}
  .prereq-conn-line {{ width: 2px; height: 10px; background: #475569; }}
  .prereq-conn-head {{
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #475569;
  }}

  /* ── Arrow between groups ── */
  .arrow {{ display: flex; flex-direction: column; align-items: center; height: 30px; }}
  .arrow-line {{ width: 2px; height: 19px;
                  background: linear-gradient(to bottom, #475569, #64748b); }}
  .arrow-head {{ width: 0; height: 0;
                  border-left: 5px solid transparent;
                  border-right: 5px solid transparent;
                  border-top: 6px solid #64748b; }}

  /* ── Legend ── */
  .legend {{
    display: flex; flex-wrap: wrap; justify-content: center;
    gap: 14px; margin-top: 22px; padding: 12px 16px;
    background: #1e293b; border-radius: 8px; border: 1px solid #334155;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 11.5px; color: #cbd5e1; }}
  .legend-dot {{ width: 14px; height: 14px; border-radius: 3px; border: 1.5px solid; }}
</style>
</head>
<body>
<div class="fc-title">Skill Acquisition Roadmap</div>
<div class="flowchart" id="fc"></div>

<div class="legend">
  <div class="legend-item">
    <div class="legend-dot" style="background:#22c55e; border-color:#16a34a;"></div>
    Must Learn
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:#fef08a; border-color:#eab308;"></div>
    Should Learn
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:#ffffff; border-color:#d1d5db;"></div>
    Nice to Know
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:#bbf7d0; border-color:#22c55e;"></div>
    Already Known
  </div>
  <div class="legend-item">
    <div class="legend-dot" style="background:#1e293b; border-color:#475569;"></div>
    Prerequisite (to learn)
  </div>
</div>

<script>
const nodes = {nodes_json};
const fc = document.getElementById('fc');

nodes.forEach((n, i) => {{
  const grp = document.createElement('div');
  grp.className = 'skill-group';

  // ── Prerequisites row ──
  if (n.prereqs && n.prereqs.length > 0) {{
    const prow = document.createElement('div');
    prow.className = 'prereq-row';
    n.prereqs.forEach(pr => {{
      const pb = document.createElement('div');
      pb.className = 'prereq-box ' + (pr.known ? 'prereq-known' : 'prereq-needed');
      let ph = '<span class="prereq-check">' + (pr.known ? '✅' : '📌') + '</span> ';
      ph += '<span class="prereq-name">' + pr.name + '</span>';
      if (pr.desc) ph += '<br><span class="prereq-desc">' + pr.desc + '</span>';
      pb.innerHTML = ph;
      prow.appendChild(pb);
    }});
    grp.appendChild(prow);

    // Connector arrow from prereqs to main node
    const conn = document.createElement('div');
    conn.className = 'prereq-connector';
    conn.innerHTML = '<div class="prereq-conn-line"></div><div class="prereq-conn-head"></div>';
    grp.appendChild(conn);
  }}

  // ── Main skill node ──
  const box = document.createElement('div');
  box.className = 'node-box';
  box.style.background = n.color;
  box.style.borderLeftColor = n.border;
  box.style.color = n.textColor;

  let h = '<div class="node-num">' + (i + 1) + '</div>';
  h += '<div class="node-header"><div class="node-skill">' + n.skill + '</div>';
  h += '<div class="node-badges">';
  if (n.category) h += '<span class="badge badge-cat">' + n.category.replace('_', ' ') + '</span>';
  if (n.proficiency) h += '<span class="badge badge-prof">' + n.proficiency + '</span>';
  h += '</div></div>';

  if (n.action) h += '<div class="node-action">' + n.action + '</div>';
  if (n.why) h += '<div class="node-why">' + n.why + '</div>';

  let meta = [];
  if (n.timeline) meta.push('⏱ ' + n.timeline);
  if (n.hours) meta.push('~' + n.hours + ' hrs');
  if (n.priority) meta.push(
    (n.priority === 'critical' ? '🔴' : n.priority === 'high' ? '🟠' :
     n.priority === 'medium' ? '🟡' : '🟢') + ' ' + n.priority
  );
  if (meta.length) h += '<div class="node-meta">' + meta.join(' &middot; ') + '</div>';

  // Resources
  if (n.resources && n.resources.length > 0) {{
    h += '<div class="node-resources"><div class="node-resources-title">RESOURCES</div>';
    n.resources.forEach(r => {{
      if (r.url) {{
        h += '<a class="res-link" href="' + r.url + '" target="_blank" rel="noopener">'
             + r.title + '</a>';
      }} else {{
        h += '<span class="res-link" style="text-decoration:none;">' + r.title + '</span>';
      }}
      if (r.type) h += '<span class="res-tag">[' + r.type + ']</span> ';
    }});
    h += '</div>';
  }}

  box.innerHTML = h;
  grp.appendChild(box);
  fc.appendChild(grp);

  // Arrow to next group
  if (i < nodes.length - 1) {{
    const arrow = document.createElement('div');
    arrow.className = 'arrow';
    arrow.innerHTML = '<div class="arrow-line"></div><div class="arrow-head"></div>';
    fc.appendChild(arrow);
  }}
}});
</script>
</body>
</html>"""
    return html


# ---------------------------------------------------------------------------
# Page render
# ---------------------------------------------------------------------------

def render():
    render_page_header("Skill Gap Analysis", "Identify gaps and get a personalized learning path")

    r_res = api("GET", "/resume/")
    r_jobs = api("GET", "/jobs/")
    if not r_res or not r_jobs:
        return

    resumes = r_res.json() if r_res.ok else []
    jobs = r_jobs.json() if r_jobs.ok else []

    if not resumes:
        render_empty_state(None, "No resumes", "Upload a resume first.")
        return
    if not jobs:
        render_empty_state(None, "No jobs", "Add a job description first.")
        return

    c1, c2 = st.columns(2)
    with c1:
        resume_opts = {f"{r.get('original_filename', 'Resume')} (#{r['id']})": r["id"] for r in resumes}
        sel_r = st.selectbox("Resume", list(resume_opts.keys()))
    with c2:
        job_opts = {f"{j.get('job_title', 'Job')} @ {j.get('company_name', '?')} (#{j['id']})": j["id"] for j in jobs}
        sel_j = st.selectbox("Job", list(job_opts.keys()))

    if st.button("📊 Analyze Skill Gap", use_container_width=True):
        with st.spinner("Running AI skill gap analysis..."):
            r = api("POST", "/advanced/skillgap", timeout=600,
                    params={"resume_id": resume_opts[sel_r], "job_id": job_opts[sel_j]})
        if r and r.ok:
            st.session_state["skillgap_result"] = r.json()
        elif r:
            detail = ""
            try:
                detail = r.json().get("detail", "")
            except Exception:
                detail = f"HTTP {r.status_code}"
            if r.status_code in (429, 503) or "quota" in detail.lower() or "api key" in detail.lower():
                st.error(
                    "🔑 **API Key Issue** — Your Gemini API key quota may be exhausted or the key is missing. "
                    "Go to **Settings** to check your API key, or wait a few minutes and try again."
                )
            else:
                st.error(detail or "Analysis failed.")

    result = st.session_state.get("skillgap_result")
    if not result:
        return

    st.markdown("---")

    # ── Skills summary ──────────────────────────────────────────────────
    col_have, col_gap = st.columns(2)
    with col_have:
        matched = result.get("matched_skills") or []
        if matched:
            st.markdown("""
<div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
            font-weight:600;margin-bottom:0.4rem;font-family:'Inter',sans-serif;">✅ Skills You Have</div>
""", unsafe_allow_html=True)
            badges = ""
            for sk in matched:
                badges += (
                    f'<span style="display:inline-block;padding:0.2rem 0.65rem;border-radius:16px;'
                    f'font-size:0.73rem;font-weight:600;background:rgba(34,197,94,0.1);'
                    f'color:#86EFAC;border:1px solid rgba(34,197,94,0.25);margin:2px;'
                    f'font-family:Inter,sans-serif;">{sk}</span>'
                )
            st.markdown(badges, unsafe_allow_html=True)
    with col_gap:
        missing = result.get("missing_skills") or []
        if missing:
            st.markdown("""
<div style="font-size:0.7rem;color:#6B6B8D;text-transform:uppercase;letter-spacing:0.08em;
            font-weight:600;margin-bottom:0.4rem;font-family:'Inter',sans-serif;">🎯 Skills to Acquire</div>
""", unsafe_allow_html=True)
            badges = ""
            for sk in missing:
                badges += (
                    f'<span style="display:inline-block;padding:0.2rem 0.65rem;border-radius:16px;'
                    f'font-size:0.73rem;font-weight:600;background:rgba(239,68,68,0.1);'
                    f'color:#FCA5A5;border:1px solid rgba(239,68,68,0.25);margin:2px;'
                    f'font-family:Inter,sans-serif;">{sk}</span>'
                )
            st.markdown(badges, unsafe_allow_html=True)

    severity = result.get("skill_gap_severity", "")
    if severity:
        sev_map = {
            "low":      ("#22c55e", "rgba(34,197,94,0.08)",  "🟢 Low"),
            "medium":   ("#f59e0b", "rgba(245,158,11,0.08)", "🟡 Medium"),
            "high":     ("#f97316", "rgba(249,115,22,0.08)", "🟠 High"),
            "critical": ("#ef4444", "rgba(239,68,68,0.08)",  "🔴 Critical"),
        }
        color, bg, label = sev_map.get(severity.lower(), ("#8B8BA8", "rgba(19,19,43,0.4)", f"⚪ {severity.title()}"))
        st.markdown(f"""
<div style="background:{bg};border:1px solid {color}30;border-radius:10px;
            padding:0.6rem 1rem;margin:0.8rem 0;display:inline-block;">
  <span style="font-size:0.78rem;font-weight:700;color:{color};
               font-family:'Inter',sans-serif;">Gap Severity: {label}</span>
</div>
""", unsafe_allow_html=True)

    # ── Learning Roadmap (flowchart) ────────────────────────────────────
    if result.get("learning_roadmap"):
        roadmap = result["learning_roadmap"]
        st.markdown("---")
        st.markdown("#### 🗺️ Learning Roadmap")
        st.caption(
            "Each skill shows its **prerequisites** above it. "
            "Green = must-learn, yellow = should-learn, white = nice-to-know. "
            "Prerequisites marked ✅ are skills you already have."
        )

        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_roadmap = sorted(
            roadmap,
            key=lambda s: priority_order.get(
                (s.get("priority", "medium") if isinstance(s, dict) else "medium").lower(), 2
            )
        )

        chart_html = _build_roadmap_flowchart(
            sorted_roadmap,
            matched_skills=result.get("matched_skills", []),
            missing_skills=result.get("missing_skills", []),
        )
        # Height: base + per-node (with prereqs taking extra space)
        n_steps = len(sorted_roadmap)
        has_prereqs = any(
            isinstance(s, dict) and s.get("prerequisites")
            for s in sorted_roadmap
        )
        per_node = 160 if has_prereqs else 120
        chart_height = min(max(n_steps * per_node + 140, 500), 2000)
        components.html(chart_html, height=chart_height, scrolling=True)

    # ── Quick Wins ──────────────────────────────────────────────────────
    # Separate certification-like objects that the LLM may have placed
    # inside quick_wins so they render in the dedicated Certifications section.
    raw_qw = result.get("quick_wins") or []
    clean_qw = []
    extra_certs = []
    for qw in raw_qw:
        if isinstance(qw, dict) and (qw.get("provider") or qw.get("covers_skills")):
            extra_certs.append(qw)
        else:
            clean_qw.append(qw)
    # Merge extracted certs into the certifications list
    if extra_certs:
        existing_certs = result.get("certifications") or []
        result["certifications"] = existing_certs + extra_certs

    if clean_qw:
        st.markdown("---")
        st.markdown("#### ⚡ Quick Wins (1-2 weeks)")
        for qw in clean_qw:
            if isinstance(qw, dict):
                label = qw.get("name") or qw.get("skill") or qw.get("action") or str(qw)
                extra = qw.get("timeline", "")
                st.markdown(f"""
<div style="background:rgba(34,197,94,0.05);border-left:3px solid #22c55e;
            border-radius:0 8px 8px 0;padding:0.5rem 0.8rem;margin-bottom:0.3rem;
            font-size:0.83rem;color:#B0B0CC;font-family:'Inter',sans-serif;">
  {label}{f' — <em>{extra}</em>' if extra else ''}
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div style="background:rgba(34,197,94,0.05);border-left:3px solid #22c55e;
            border-radius:0 8px 8px 0;padding:0.5rem 0.8rem;margin-bottom:0.3rem;
            font-size:0.83rem;color:#B0B0CC;font-family:'Inter',sans-serif;">
  {qw}
</div>
""", unsafe_allow_html=True)

    # ── Long-term Goals ─────────────────────────────────────────────────
    if result.get("long_term_goals"):
        st.markdown("---")
        st.markdown("#### 🎯 Long-term Goals")
        for lg in result["long_term_goals"]:
            st.markdown(f"""
<div style="background:rgba(99,102,241,0.05);border-left:3px solid #6366F1;
            border-radius:0 8px 8px 0;padding:0.5rem 0.8rem;margin-bottom:0.3rem;
            font-size:0.83rem;color:#B0B0CC;font-family:'Inter',sans-serif;">
  {lg}
</div>
""", unsafe_allow_html=True)

    # ── Certifications ──────────────────────────────────────────────────
    if result.get("certifications"):
        st.markdown("---")
        st.markdown("#### 🏆 Recommended Certifications")
        st.caption("Matched to your missing skills. Only real, verifiable certifications from known providers.")
        for cert in result["certifications"]:
            if isinstance(cert, dict):
                name = cert.get("name", "")
                provider = cert.get("provider", "")
                url = cert.get("url", "")
                priority = cert.get("priority", "")
                timeline = cert.get("timeline", "")
                covers = cert.get("covers_skills") or []
                link = f"[{name}]({url})" if url else name
                extra = ""
                if provider:
                    extra += f" — {provider}"
                if priority:
                    prio_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    extra += f" {prio_icons.get(priority.lower(), '')} {priority}"
                if timeline:
                    extra += f" · {timeline}"
                st.markdown(f"- {link}{extra}")
                if covers:
                    st.caption(f"  Covers: {', '.join(covers)}")
            else:
                st.markdown(f"- {cert}")

    # ── Resume Update Tips ──────────────────────────────────────────────
    if result.get("resume_update_tips"):
        st.markdown("---")
        st.markdown("#### 📝 Resume Update Tips")
        for tip in result["resume_update_tips"]:
            st.markdown(f"""
<div style="background:rgba(245,158,11,0.05);border-left:3px solid #f59e0b;
            border-radius:0 8px 8px 0;padding:0.5rem 0.8rem;margin-bottom:0.3rem;
            font-size:0.83rem;color:#B0B0CC;font-family:'Inter',sans-serif;">
  {tip}
</div>
""", unsafe_allow_html=True)
