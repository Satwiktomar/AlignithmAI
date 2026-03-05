import json
import streamlit as st
import streamlit.components.v1 as components
from utils.auth import api
from utils.styles import render_page_header


# ---------------------------------------------------------------------------
# roadmap.sh-style tree renderer  (gold/yellow nodes, blue connectors)
# ---------------------------------------------------------------------------

def _build_tree_roadmap_html(data: dict) -> str:
    """
    Build a roadmap.sh-style branching tree from structured sections.

    Colour palette (matches the reference image):
      Section headers : gold gradient (#f0c27a → #e0a030)
      Sub-topic labels: #fbbf24 amber
      Skill boxes     : #fef08a yellow (must_learn), #fef9c3 light-yellow
                        (should_learn), #ffffff white (nice_to_know)
      Connectors      : #60a5fa blue
      Related pills   : #3b82f6 blue
    """
    title = data.get("title", "Learning Roadmap")
    description = data.get("description", "")
    sections = data.get("sections") or []

    # Normalise: support both new (sub_topics) and old (skills) prompt formats
    normalised = []
    for sec in sections[:14]:
        sub_topics = sec.get("sub_topics")
        if not sub_topics:
            # Fall back: wrap flat skills list as a single sub_topic
            flat_skills = sec.get("skills") or []
            sub_topics = [{"name": sec.get("name", ""), "skills": flat_skills}]
        cleaned_subs = []
        for st_item in (sub_topics or [])[:5]:
            skills = []
            for sk in (st_item.get("skills") or [])[:6]:
                if isinstance(sk, dict):
                    resources = []
                    for r in (sk.get("resources") or [])[:2]:
                        if isinstance(r, dict):
                            resources.append({"t": r.get("title", ""), "u": r.get("url", ""), "k": r.get("type", "")})
                    skills.append({
                        "n": sk.get("name", ""),
                        "p": sk.get("priority", "should_learn"),
                        "d": (sk.get("description") or "")[:100],
                        "h": sk.get("estimated_hours", ""),
                        "r": resources,
                    })
                elif isinstance(sk, str):
                    skills.append({"n": sk, "p": "should_learn", "d": "", "h": "", "r": []})
            if skills:
                cleaned_subs.append({"name": st_item.get("name", ""), "skills": skills})
        normalised.append({
            "name": sec.get("name", f"Section {sec.get('order', '')}"),
            "desc": (sec.get("description") or "")[:120],
            "subs": cleaned_subs,
        })

    related = data.get("related_roadmaps") or []

    payload = json.dumps({"sections": normalised, "related": related[:8]})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background:#0f172a;
  font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
  color:#e2e8f0;
  padding:20px 8px 50px;
}}

/* ── Title ── */
.rm-title {{ text-align:center; font-size:22px; font-weight:800; color:#f1f5f9;
             margin-bottom:4px; letter-spacing:.5px; }}
.rm-desc  {{ text-align:center; font-size:12px; color:#94a3b8; margin-bottom:24px;
             max-width:640px; margin-left:auto; margin-right:auto; line-height:1.5; }}

/* ── Central spine ── */
.tree {{ display:flex; flex-direction:column; align-items:center; }}

/* ── Section header ── */
.sec-head {{
  background: linear-gradient(135deg, #f0c27a, #e0a030);
  color: #422006;
  padding: 10px 28px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  text-align: center;
  max-width: 320px;
  box-shadow: 0 2px 8px rgba(0,0,0,.25);
  position: relative;
}}
.sec-desc {{ font-size:10px; opacity:.7; margin-top:2px; font-weight:400; }}

/* ── Vertical connector (blue) ── */
.v-conn {{ width:3px; height:22px; background:#60a5fa; }}
.v-conn-long {{ width:3px; height:32px; background:#60a5fa; }}

/* ── Sub-topic row ── */
.sub-row {{
  display:flex;
  justify-content:center;
  align-items:flex-start;
  gap:16px;
  flex-wrap:wrap;
  max-width:900px;
  position:relative;
}}

/* ── Sub-topic box ── */
.sub-box {{
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:6px;
  min-width:130px;
  max-width:260px;
}}
.sub-label {{
  background:#fbbf24;
  color:#422006;
  padding:6px 16px;
  border-radius:8px;
  font-size:12px;
  font-weight:700;
  text-align:center;
  box-shadow:0 1px 4px rgba(0,0,0,.2);
  white-space:nowrap;
}}
.sub-conn {{ width:2px; height:10px; background:#60a5fa; }}

/* ── Skill leaf boxes ── */
.skill-row {{
  display:flex; gap:6px; flex-wrap:wrap; justify-content:center;
}}
.sk {{
  padding:5px 11px;
  border-radius:6px;
  font-size:11px;
  font-weight:600;
  border:1.5px solid;
  cursor:default;
  transition: transform .1s;
  text-align:center;
  max-width:180px;
  line-height:1.3;
}}
.sk:hover {{ transform:translateY(-2px); }}
.sk-must   {{ background:#fef08a; border-color:#eab308; color:#422006; }}
.sk-should {{ background:#fef9c3; border-color:#fbbf24; color:#78350f; }}
.sk-nice   {{ background:#ffffff; border-color:#d1d5db; color:#374151; }}
.sk-desc {{ font-size:9px; font-weight:400; opacity:.7; margin-top:2px; }}
.sk-hrs  {{ font-size:8px; font-weight:400; opacity:.5; }}

/* ── Tooltip ── */
.sk[title] {{ position:relative; }}

/* ── Horizontal branch line ── */
.h-branch {{
  height:2px;
  background:#60a5fa;
  position:absolute;
  top:0;
  z-index:0;
}}

/* ── Related roadmaps ── */
.related-wrap {{
  margin-top:32px;
  text-align:center;
}}
.related-title {{
  font-size:12px;
  color:#94a3b8;
  margin-bottom:10px;
  border:1px dashed #475569;
  display:inline-block;
  padding:4px 14px;
  border-radius:6px;
}}
.related-pills {{ display:flex; flex-wrap:wrap; justify-content:center; gap:8px; }}
.rpill {{
  background:#3b82f6;
  color:#fff;
  padding:5px 14px;
  border-radius:6px;
  font-size:11px;
  font-weight:600;
  cursor:default;
}}

/* ── Legend ── */
.legend {{
  display:flex; flex-wrap:wrap; justify-content:center;
  gap:14px; margin-top:28px; padding:10px 14px;
  background:#1e293b; border-radius:8px; border:1px solid #334155;
}}
.legend-item {{ display:flex; align-items:center; gap:5px; font-size:11px; color:#cbd5e1; }}
.legend-dot {{ width:14px; height:14px; border-radius:3px; border:1.5px solid; }}
</style>
</head>
<body>

<div class="rm-title">{title}</div>
<div class="rm-desc">{description}</div>

<div class="tree" id="tree"></div>

<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:linear-gradient(135deg,#f0c27a,#e0a030);border-color:#e0a030;"></div> Section</div>
  <div class="legend-item"><div class="legend-dot" style="background:#fbbf24;border-color:#d97706;"></div> Sub-topic</div>
  <div class="legend-item"><div class="legend-dot" style="background:#fef08a;border-color:#eab308;"></div> Must Learn</div>
  <div class="legend-item"><div class="legend-dot" style="background:#fef9c3;border-color:#fbbf24;"></div> Should Learn</div>
  <div class="legend-item"><div class="legend-dot" style="background:#ffffff;border-color:#d1d5db;"></div> Nice to Know</div>
</div>

<script>
const DATA = {payload};
const tree = document.getElementById('tree');

function vc(cls) {{
  const d = document.createElement('div');
  d.className = cls || 'v-conn';
  return d;
}}

DATA.sections.forEach((sec, si) => {{
  // Section header
  const sh = document.createElement('div');
  sh.className = 'sec-head';
  sh.innerHTML = sec.name + (sec.desc ? '<div class="sec-desc">' + sec.desc + '</div>' : '');
  tree.appendChild(sh);

  tree.appendChild(vc('v-conn'));

  // Sub-topic row
  if (sec.subs && sec.subs.length) {{
    const row = document.createElement('div');
    row.className = 'sub-row';

    sec.subs.forEach(sub => {{
      const box = document.createElement('div');
      box.className = 'sub-box';

      // Sub-topic label
      const lbl = document.createElement('div');
      lbl.className = 'sub-label';
      lbl.textContent = sub.name;
      box.appendChild(lbl);

      box.appendChild(vc('sub-conn'));

      // Skill leaves
      const sr = document.createElement('div');
      sr.className = 'skill-row';
      (sub.skills || []).forEach(sk => {{
        const s = document.createElement('div');
        const p = (sk.p || 'should_learn').toLowerCase();
        let cls = 'sk sk-should';
        if (p === 'must_learn' || p === 'critical' || p === 'high') cls = 'sk sk-must';
        else if (p === 'nice_to_know' || p === 'low') cls = 'sk sk-nice';
        s.className = cls;

        let inner = sk.n;
        if (sk.d) inner += '<div class="sk-desc">' + sk.d + '</div>';
        if (sk.h) inner += '<div class="sk-hrs">~' + sk.h + ' hrs</div>';
        s.innerHTML = inner;

        // Tooltip with resources
        if (sk.r && sk.r.length) {{
          const tips = sk.r.map(r => r.t + (r.k ? ' [' + r.k + ']' : '')).join(' | ');
          s.title = tips;
        }}

        sr.appendChild(s);
      }});
      box.appendChild(sr);
      row.appendChild(box);
    }});
    tree.appendChild(row);
  }}

  // Arrow to next section
  if (si < DATA.sections.length - 1) {{
    tree.appendChild(vc('v-conn-long'));
  }}
}});

// Related roadmaps
if (DATA.related && DATA.related.length) {{
  tree.appendChild(vc('v-conn-long'));
  const wrap = document.createElement('div');
  wrap.className = 'related-wrap';
  wrap.innerHTML = '<div class="related-title">Visit the following roadmaps to keep learning</div>';
  const pills = document.createElement('div');
  pills.className = 'related-pills';
  DATA.related.forEach(r => {{
    const p = document.createElement('div');
    p.className = 'rpill';
    p.textContent = r;
    pills.appendChild(p);
  }});
  wrap.appendChild(pills);
  tree.appendChild(wrap);
}}
</script>
</body>
</html>"""
    return html


# ---------------------------------------------------------------------------
# Page render
# ---------------------------------------------------------------------------

def render():
    render_page_header("Roadmap Builder", "Generate detailed learning roadmaps for any role, technology, or skill")

    st.markdown(
        "Enter a **job role** (e.g. ML Engineer), **technology** (e.g. Blockchain), "
        "**framework** (e.g. React), **skill** (e.g. System Design), or paste a **full job description** "
        "to generate a comprehensive roadmap."
    )

    # ── Previously cached roadmaps ──────────────────────────────────────
    cached_list = []
    try:
        cr = api("GET", "/advanced/cached-roadmaps")
        if cr and cr.ok:
            cached_list = cr.json()
    except Exception:
        pass

    if cached_list:
        st.markdown("#### 📂 Your Saved Roadmaps")
        cols = st.columns([4, 2, 1])
        cols[0].markdown("**Topic**")
        cols[1].markdown("**Created**")
        cols[2].markdown("")
        for item in cached_list[:20]:
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(item.get("topic", ""))
            created = item.get("created_at", "")
            if created:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created)
                    created = dt.strftime("%b %d, %Y")
                except Exception:
                    pass
            c2.write(created)
            if c3.button("Load", key=f"load_{item['id']}"):
                with st.spinner("Loading cached roadmap..."):
                    r = api("POST", "/advanced/roadmap-builder", json={
                        "topic": item["topic"],
                        "context": "general",
                        "force_new": False,
                    })
                if r and r.ok:
                    st.session_state["roadmap_result"] = r.json()
                    st.rerun()
        st.markdown("---")

    # Input mode selector
    input_mode = st.radio(
        "Input type",
        ["Topic / Role / Technology", "Job Description"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if input_mode == "Topic / Role / Technology":
        topic = st.text_input(
            "What do you want to learn?",
            placeholder="e.g. Machine Learning Engineer, React, Blockchain, System Design",
            key="rm_topic",
        )
        context = "Generate a comprehensive roadmap for this topic/role/technology."
    else:
        topic = st.text_area(
            "Paste the job description",
            placeholder="Paste the full job description here...",
            height=150,
            key="rm_jd",
        )
        context = "Generate a roadmap based on this job description. Focus on the skills and technologies required."

    col_gen, col_new = st.columns([3, 2])
    gen_clicked = col_gen.button("🗺️ Generate Roadmap", use_container_width=True)
    force_new = col_new.button("🔄 Generate New (skip cache)", use_container_width=True)

    if gen_clicked or force_new:
        if not topic or len(topic.strip()) < 3:
            st.warning("Please enter a topic or job description (at least 3 characters).")
        else:
            with st.spinner("Generating your roadmap — this may take 2-3 minutes for new topics..."):
                r = api("POST", "/advanced/roadmap-builder", json={
                    "topic": topic.strip(),
                    "context": context,
                    "force_new": force_new,
                })
            if r and r.ok:
                st.session_state["roadmap_result"] = r.json()
            elif r:
                detail = ""
                try:
                    detail = r.json().get("detail", "")
                except Exception:
                    detail = f"HTTP {r.status_code}"
                if r.status_code in (429, 503) or "quota" in detail.lower() or "api key" in detail.lower():
                    st.error(
                        "🔑 **API Key Issue** — Your Gemini API key quota may be exhausted. "
                        "Go to **Settings** to check, or wait a few minutes and try again."
                    )
                else:
                    st.error(detail or "Roadmap generation failed.")

    result = st.session_state.get("roadmap_result")
    if not result:
        return

    # Handle case where result is a list or has an error
    if isinstance(result, dict) and result.get("error"):
        st.error(
            "⚠️ **Roadmap generation failed** — the AI response couldn't be parsed. "
            "This often happens when using a local model or when the API quota is exhausted. "
            "Try again in a moment, or check your API key in **Settings**."
        )
        return

    # Show "cached" badge if loaded from cache
    if isinstance(result, dict) and result.get("cached"):
        st.info("📦 This roadmap was loaded from cache. Click **🔄 Generate New** to create a fresh one.")

    st.markdown("---")

    # ── Header info ─────────────────────────────────────────────────────
    title = result.get("title", "Learning Roadmap")
    desc = result.get("description", "")
    months = result.get("estimated_total_months", "")

    st.markdown(f"### {title}")
    if desc:
        st.caption(desc)
    if months:
        st.markdown(f"**Estimated timeline:** ~{months} months (part-time)")

    # ── Tree flowchart ──────────────────────────────────────────────────
    sections = result.get("sections") or []
    if sections:
        # Estimate height: section headers + sub-topics + skills
        total_subs = sum(
            len(s.get("sub_topics") or s.get("skills") or [])
            for s in sections
        )
        total_skills = sum(
            sum(len(st_item.get("skills") or []) for st_item in (s.get("sub_topics") or [{"skills": s.get("skills", [])}]))
            for s in sections
        )
        chart_height = min(max(
            len(sections) * 110 + total_subs * 60 + total_skills * 28 + 250
        , 600), 5000)

        chart_html = _build_tree_roadmap_html(result)
        components.html(chart_html, height=chart_height, scrolling=True)

    # ── Certifications ──────────────────────────────────────────────────
    certs = result.get("certifications") or []
    if certs:
        st.markdown("---")
        st.markdown("#### 🏆 Recommended Certifications")
        for cert in certs:
            if isinstance(cert, dict):
                name = cert.get("name", "")
                provider = cert.get("provider", "")
                url = cert.get("url", "")
                covers = cert.get("covers_section", "")
                priority = cert.get("priority", "")
                link = f"[{name}]({url})" if url else name
                extra = ""
                if provider:
                    extra += f" — {provider}"
                if priority:
                    prio_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    extra += f" {prio_icons.get(priority.lower(), '')} {priority}"
                if covers:
                    extra += f" · covers: {covers}"
                st.markdown(f"- {link}{extra}")
            else:
                st.markdown(f"- {cert}")

    # ── Career progression ──────────────────────────────────────────────
    progression = result.get("career_progression") or []
    if progression:
        st.markdown("---")
        st.markdown("#### 📈 Career Progression")
        prog_str = " → ".join(f"**{p}**" for p in progression)
        st.markdown(prog_str)

    # ── Related roadmaps ────────────────────────────────────────────────
    related = result.get("related_roadmaps") or []
    if related:
        st.markdown("---")
        st.markdown("#### 🔗 Related Roadmaps to Explore")
        st.write(", ".join(related))
