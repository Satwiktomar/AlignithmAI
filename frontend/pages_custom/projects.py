import re
import base64
from calendar import month_name
from datetime import datetime

import requests as http_requests
import streamlit as st
from utils.auth import api
from utils.styles import render_page_header, render_empty_state, score_color


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

def _parse_github_owner_repo(url: str):
    """Return (owner, repo) from a GitHub URL, or raise ValueError."""
    url = url.strip().rstrip("/")
    match = re.search(r"github\.com[:/]([^/]+)/([^/\s]+?)(?:\.git)?$", url)
    if not match:
        raise ValueError(
            "Could not parse a GitHub repository from the URL. "
            "Expected format: https://github.com/owner/repo"
        )
    return match.group(1), match.group(2)


def _gh_get(path: str, params: dict = None) -> dict | None:
    """GET a GitHub API endpoint. Returns parsed JSON or None on 404."""
    headers = {"Accept": "application/vnd.github+json"}
    r = http_requests.get(
        f"https://api.github.com{path}",
        headers=headers,
        params=params or {},
        timeout=10,
    )
    if r.status_code == 404:
        return None
    if r.status_code == 403:
        raise RuntimeError(
            "GitHub API rate limit reached or repository is private. "
            "Try again later or make sure the repository is public."
        )
    if not r.ok:
        raise RuntimeError(f"GitHub API returned HTTP {r.status_code}.")
    return r.json()


def _gh_get_list(path: str, params: dict = None, max_pages: int = 3) -> list:
    """Paginated GET returning a flat list."""
    results = []
    p = dict(params or {})
    p.setdefault("per_page", 100)
    for page in range(1, max_pages + 1):
        p["page"] = page
        data = _gh_get(path, p)
        if not data:
            break
        if isinstance(data, list):
            results.extend(data)
            if len(data) < p["per_page"]:
                break
        else:
            results.append(data)
            break
    return results


def _truncate(text: str, max_chars: int = 600) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


# ---------------------------------------------------------------------------
# Deep contribution analysis
# ---------------------------------------------------------------------------

FEATURE_KEYWORDS = [
    "add", "added", "implement", "implemented", "create", "created",
    "build", "built", "introduce", "introduced", "develop", "developed",
    "feat", "feature", "new",
]
FIX_KEYWORDS = [
    "fix", "fixed", "bug", "patch", "resolve", "resolved", "repair",
    "correct", "corrected",
]
REFACTOR_KEYWORDS = [
    "refactor", "refactored", "improve", "improved", "optimize", "optimized",
    "clean", "cleaned", "simplify",
]
REVIEW_KEYWORDS = ["review", "reviewed", "merge", "merged", "approve", "approved"]


def _classify_commit(msg: str) -> str:
    m = msg.lower()
    if any(k in m for k in FEATURE_KEYWORDS):
        return "feature"
    if any(k in m for k in FIX_KEYWORDS):
        return "fix"
    if any(k in m for k in REFACTOR_KEYWORDS):
        return "improvement"
    return "other"


def _extract_contributions(owner: str, repo: str) -> dict:
    """
    Fetch commits authored by `owner` and PR activity, then return
    a structured contribution summary.
    """
    commits_raw = _gh_get_list(
        f"/repos/{owner}/{repo}/commits",
        {"author": owner, "per_page": 100},
        max_pages=3,
    )

    features, fixes, improvements, other_msgs = [], [], [], []
    for c in commits_raw:
        msg = c.get("commit", {}).get("message", "").split("\n")[0].strip()
        if not msg:
            continue
        kind = _classify_commit(msg)
        # Capitalise and strip common prefixes like "feat:", "fix:", "chore:" etc.
        clean_msg = re.sub(r"^(feat|fix|chore|docs|test|refactor|style|perf|ci|build)[:\s!()]+", "", msg, flags=re.I).strip().capitalize()
        if kind == "feature":
            features.append(clean_msg)
        elif kind == "fix":
            fixes.append(clean_msg)
        elif kind == "improvement":
            improvements.append(clean_msg)
        else:
            other_msgs.append(clean_msg)

    # Pull requests the owner opened
    prs_raw = _gh_get_list(
        f"/repos/{owner}/{repo}/pulls",
        {"state": "all", "creator": owner, "per_page": 50},
        max_pages=2,
    )
    pr_titles = [pr.get("title", "").strip() for pr in prs_raw if pr.get("title")]

    # Issues the owner opened
    issues_raw = _gh_get_list(
        f"/repos/{owner}/{repo}/issues",
        {"state": "all", "creator": owner, "per_page": 30},
        max_pages=1,
    )
    issue_titles = [
        i.get("title", "").strip()
        for i in issues_raw
        if i.get("title") and not i.get("pull_request")  # skip PRs listed as issues
    ]

    return {
        "total_commits": len(commits_raw),
        "features": features[:8],
        "fixes": fixes[:6],
        "improvements": improvements[:6],
        "pr_titles": pr_titles[:6],
        "issue_titles": issue_titles[:4],
    }


def fetch_github_repo_info(repo_url: str) -> dict:
    """
    Fetch repository metadata + contributor analysis.
    Returns a dict ready to pre-fill the form.
    """
    owner, repo = _parse_github_owner_repo(repo_url)

    # 1 — core repo metadata
    repo_data = _gh_get(f"/repos/{owner}/{repo}")
    if repo_data is None:
        raise ValueError(
            "Repository not found. It may be private or the URL is incorrect."
        )

    title = repo_data.get("name", repo).replace("-", " ").replace("_", " ").title()
    repo_description = repo_data.get("description") or ""
    primary_language = repo_data.get("language") or ""
    topics: list[str] = repo_data.get("topics", [])
    pushed_at = repo_data.get("pushed_at", "")

    # 2 — language breakdown
    lang_data = _gh_get(f"/repos/{owner}/{repo}/languages") or {}
    languages = list(lang_data.keys())

    # 3 — README for richer description
    readme_text = ""
    readme_data = _gh_get(f"/repos/{owner}/{repo}/readme")
    if readme_data and readme_data.get("encoding") == "base64":
        raw = base64.b64decode(readme_data["content"]).decode("utf-8", errors="replace")
        lines = [
            re.sub(r"[#\[\]!*`>|]", "", ln).strip()
            for ln in raw.splitlines()
            if ln.strip() and not ln.strip().startswith("<!--")
        ]
        readme_text = _truncate(" ".join(filter(None, lines)), 600)

    # 4 — dependency hints
    dep_skills: list[str] = []
    known_frameworks = {
        "react": "React", "vue": "Vue.js", "angular": "Angular",
        "svelte": "Svelte", "next": "Next.js", "nuxt": "Nuxt",
        "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
        "express": "Express", "nestjs": "NestJS", "spring": "Spring Boot",
        "rails": "Rails", "pytorch": "PyTorch", "tensorflow": "TensorFlow",
        "scikit-learn": "Scikit-Learn", "pandas": "Pandas", "numpy": "NumPy",
        "langchain": "LangChain", "openai": "OpenAI", "anthropic": "Anthropic",
        "playwright": "Playwright", "selenium": "Selenium", "redis": "Redis",
        "postgresql": "PostgreSQL", "mongodb": "MongoDB", "docker": "Docker",
    }
    for manifest in ("package.json", "requirements.txt", "pyproject.toml", "Gemfile"):
        manifest_data = _gh_get(f"/repos/{owner}/{repo}/contents/{manifest}")
        if manifest_data and manifest_data.get("encoding") == "base64":
            content = base64.b64decode(manifest_data["content"]).decode("utf-8", errors="replace").lower()
            for kw, label in known_frameworks.items():
                if kw in content and label not in dep_skills:
                    dep_skills.append(label)

    # 5 — deep contribution analysis
    contributions = _extract_contributions(owner, repo)

    # 6 — assemble skills
    skills_set: list[str] = []
    for lang in languages[:4]:
        if lang not in skills_set:
            skills_set.append(lang)
    for t in topics[:4]:
        label = t.replace("-", " ").title()
        if label not in skills_set:
            skills_set.append(label)
    for d in dep_skills[:4]:
        if d not in skills_set:
            skills_set.append(d)

    # 7 — rich description: combine README + contribution highlights
    description_parts = []
    if readme_text:
        description_parts.append(readme_text)
    elif repo_description:
        description_parts.append(repo_description)

    # Inject "what you built"
    if contributions["features"]:
        highlights = "; ".join(contributions["features"][:3])
        description_parts.append(f"Key features built: {highlights}.")
    if contributions["improvements"]:
        imps = "; ".join(contributions["improvements"][:2])
        description_parts.append(f"Improvements: {imps}.")

    description = " ".join(description_parts)

    # 8 — domain
    domain = primary_language or (topics[0].replace("-", " ").title() if topics else "")

    # 9 — approximate date from last push
    last_updated = ""
    if pushed_at:
        try:
            dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            last_updated = f"{month_name[dt.month]}, {dt.year}"
        except Exception:
            pass

    return {
        "title": title,
        "description": description,
        "skills": ", ".join(skills_set),
        "domain": domain,
        "github_url": repo_url.strip(),
        "last_updated": last_updated,
        "contributions": contributions,
    }


# ---------------------------------------------------------------------------
# LaTeX generation (template-based XYZ formula)
# ---------------------------------------------------------------------------

def _build_latex_highlights(p: dict) -> list[str]:
    """
    Build 3-4 LaTeX highlight bullet strings from a project dict.
    Uses Google XYZ formula: Accomplished X, as measured by Y, by doing Z.
    """
    bullets: list[str] = []

    desc = p.get("description") or ""
    skills = p.get("skills_json") or []
    metrics = p.get("metrics_json") or []
    domain = p.get("domain") or "software"
    title = p.get("title") or "the project"

    # Bullet 1 – main achievement from description (shortened)
    if desc:
        short_desc = desc[:220].rsplit(" ", 1)[0]
        bullets.append(short_desc + ("…" if len(desc) > 220 else ""))

    # Bullet 2 – metric-based if available
    for m in metrics[:2]:
        bullets.append(m)

    # Bullet 3 – tech stack
    if skills:
        tool_str = ", ".join(skills[:7])
        bullets.append(f"\\textbf{{Tools:}} {tool_str}.")

    # Pad to at least 2 bullets
    if len(bullets) < 2:
        bullets.insert(0, f"Built {title} — a {domain} project.")

    return bullets[:4]


def generate_project_latex(p: dict) -> str:
    """
    Generate a resume-ready LaTeX snippet for a project using the
    twocolentry / onecolentry pattern with XYZ-formula highlight bullets.
    """
    title = p.get("title", "Project")
    github_url = p.get("github_url") or ""
    # Try to infer a date string — stored in tags or metrics is not standard,
    # so we generate a placeholder from created_at if available.
    created_at = p.get("created_at") or ""
    date_str = ""
    if created_at:
        try:
            dt = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
            date_str = f"{month_name[dt.month]}, {dt.year}"
        except Exception:
            pass
    if not date_str:
        date_str = datetime.now().strftime("%B, %Y")

    # Header line
    if github_url:
        gh_short = github_url.replace("https://", "").replace("http://", "")
        header_title = f"\\textbf{{{title}}} \\hrefWithoutArrow{{{github_url}}}{{\\faGithub}}"
    else:
        header_title = f"\\textbf{{{title}}}"

    # Highlights
    raw_bullets = _build_latex_highlights(p)
    bullet_lines = "\n        ".join([f"\\item {b}" for b in raw_bullets])

    latex = f"""\
\\begin{{twocolentry}}{{
     \\textit{{({date_str})}}{{}}}}
     {header_title}
\\end{{twocolentry}}
\\vspace{{0.10 cm}}
\\begin{{onecolentry}}
    \\begin{{highlights}}
        {bullet_lines}
    \\end{{highlights}}
\\end{{onecolentry}}"""
    return latex


# ---------------------------------------------------------------------------
# Page render
# ---------------------------------------------------------------------------

def render():
    render_page_header("Projects", "Showcase your work and find which projects to highlight")

    tab_list, tab_add, tab_rank = st.tabs(["My Projects", "Add Project", "Rank for Job"])

    # ──────────────────────────────────────────────────────────────────────
    with tab_add:

        # ── Optional GitHub auto-fill section ──────────────────────────────
        with st.expander("🔗 Auto-fill from GitHub (optional)", expanded=False):
            st.caption(
                "Paste a **public** GitHub repository URL and click **Auto Extract** "
                "to deeply analyse your contributions and pre-fill the form below."
            )
            gh_input_url = st.text_input(
                "GitHub Repository URL",
                placeholder="https://github.com/owner/repo",
                key="gh_url_input",
            )
            if st.button("⚡ Auto Extract", key="gh_extract_btn"):
                if not gh_input_url.strip():
                    st.warning("Please enter a GitHub repository URL first.")
                else:
                    with st.spinner("Fetching repository info and analysing your contributions…"):
                        try:
                            extracted = fetch_github_repo_info(gh_input_url)
                            st.session_state["github_extracted"] = extracted
                            contrib = extracted.get("contributions", {})
                            st.success(
                                f"✅ Analysis complete! Found **{contrib.get('total_commits', 0)} commits** "
                                f"by you — fields pre-filled below. Review before saving."
                            )
                        except ValueError as e:
                            st.error(f"❌ Invalid URL: {e}")
                        except RuntimeError as e:
                            st.error(f"❌ GitHub API error: {e}")
                        except Exception as e:
                            st.error(f"❌ Unexpected error: {e}")

            # Show contribution breakdown if available (flat layout — no nested expanders)
            pre_contrib = st.session_state.get("github_extracted", {}).get("contributions", {})
            if pre_contrib:
                c1, c2, c3 = st.columns(3)
                c1.metric("Total commits", pre_contrib.get("total_commits", 0))
                c2.metric("Features built", len(pre_contrib.get("features", [])))
                c3.metric("PRs opened", len(pre_contrib.get("pr_titles", [])))

                if pre_contrib.get("features"):
                    st.markdown("**🛠 Features you built**")
                    for f in pre_contrib["features"][:6]:
                        st.markdown(f"- {f}")
                if pre_contrib.get("fixes"):
                    st.markdown("**🐛 Bugs you fixed**")
                    for f in pre_contrib["fixes"][:4]:
                        st.markdown(f"- {f}")
                if pre_contrib.get("improvements"):
                    st.markdown("**🔧 Improvements you made**")
                    for f in pre_contrib["improvements"][:4]:
                        st.markdown(f"- {f}")
                if pre_contrib.get("pr_titles"):
                    st.markdown("**📬 Pull requests**")
                    for t in pre_contrib["pr_titles"][:4]:
                        st.markdown(f"- {t}")

            if st.session_state.get("github_extracted"):
                if st.button("✖ Clear extracted data", key="gh_clear_btn"):
                    del st.session_state["github_extracted"]
                    st.rerun()

        _pre = st.session_state.get("github_extracted", {})

        st.markdown("---")

        # ── Existing manual form (unchanged logic) ─────────────────────────
        title = st.text_input("Project title", value=_pre.get("title", ""))
        description = st.text_area("Description", value=_pre.get("description", ""), height=120)
        domain = st.text_input(
            "Domain",
            value=_pre.get("domain", ""),
            placeholder="e.g. Machine Learning, Web Dev",
        )
        skills_raw = st.text_input(
            "Skills used (comma-separated)",
            value=_pre.get("skills", ""),
        )
        metrics_raw = st.text_input("Key metrics (comma-separated)")
        github_url = st.text_input(
            "GitHub URL (optional)",
            value=_pre.get("github_url", ""),
        )
        complexity = st.selectbox("Complexity level", ["Beginner", "Intermediate", "Advanced"])

        if st.button("Add Project", use_container_width=True):
            if not title:
                st.error("Project title is required.")
            else:
                skills_list = [s.strip() for s in skills_raw.split(",") if s.strip()]
                metrics_list = [m.strip() for m in metrics_raw.split(",") if m.strip()]
                r = api("POST", "/projects/", json={
                    "title": title,
                    "description": description,
                    "domain": domain,
                    "skills_json": skills_list,
                    "metrics_json": metrics_list,
                    "github_url": github_url,
                    "complexity_level": complexity,
                    "tags": []
                })
                if r and r.ok:
                    st.session_state.pop("github_extracted", None)
                    st.success("Project added.")
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Failed to add project."))

    # ──────────────────────────────────────────────────────────────────────
    with tab_list:
        r = api("GET", "/projects/")
        if not r or not r.ok:
            st.error("Failed to load projects.")
            return
        projects = r.json()
        if not projects:
            render_empty_state(None, "No projects yet", "Add your first project in the 'Add Project' tab.")
            return

        for p in projects:
            with st.expander(f"{p.get('title', '')}  |  {p.get('domain', '') or 'General'}"):
                if p.get("description"):
                    st.write(p["description"])
                if p.get("skills_json"):
                    st.markdown(f"**Skills:** {', '.join(p['skills_json'])}")
                if p.get("metrics_json"):
                    st.markdown(f"**Metrics:** {' | '.join(p['metrics_json'])}")
                if p.get("github_url"):
                    st.markdown(f"[GitHub]({p['github_url']})")

                # ── LaTeX export (no nested expander) ────────────────────
                st.markdown("---")
                latex_key = f"show_latex_{p['id']}"
                if st.button("📄 Show LaTeX Snippet (XYZ formula)", key=f"latex_btn_{p['id']}"):
                    st.session_state[latex_key] = not st.session_state.get(latex_key, False)
                if st.session_state.get(latex_key, False):
                    latex_code = generate_project_latex(p)
                    st.code(latex_code, language="latex")
                    st.caption(
                        "Copy this into your LaTeX resume under the **Projects** section. "
                        "Bullets follow Google's XYZ formula: *Accomplished X, as measured by Y, by doing Z.*"
                    )

                if st.button("Delete", key=f"del_proj_{p['id']}"):
                    dr = api("DELETE", f"/projects/{p['id']}")
                    if dr and dr.ok:
                        st.rerun()

    # ──────────────────────────────────────────────────────────────────────
    with tab_rank:
        r_jobs = api("GET", "/jobs/")
        if not r_jobs or not r_jobs.ok:
            st.error("Failed to load jobs.")
            return
        jobs = r_jobs.json()
        if not jobs:
            render_empty_state(None, "No jobs", "Add a job description first.")
            return

        job_opts = {f"{j.get('job_title', 'Job')} @ {j.get('company_name', '?')} (#{j['id']})": j["id"] for j in jobs}
        sel_j = st.selectbox("Select job to rank projects against", list(job_opts.keys()))

        if st.button("Rank My Projects", use_container_width=True):
            with st.spinner("Ranking projects..."):
                r = api("POST", "/projects/recommend", params={"job_id": job_opts[sel_j]})
            if r and r.ok:
                st.session_state["ranked_projects"] = r.json()
            elif r:
                st.error(r.json().get("detail", "Ranking failed."))

        ranked = st.session_state.get("ranked_projects")
        if ranked:
            st.markdown("---")
            items = ranked if isinstance(ranked, list) else ranked.get("ranked", ranked.get("projects", []))
            for i, p in enumerate(items, 1):
                score = int(float(p.get("relevance_score", p.get("score", 0))))
                reason = p.get("reason", "") or p.get("rationale", "")
                st.markdown(f"**{i}. {p.get('title', 'Project')}** — Score: {score}")
                if reason:
                    st.caption(reason)
