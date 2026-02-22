import re
from collections import Counter
from typing import Optional


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\s+#]", " ", text.lower())


def extract_ngrams(text: str, n: int = 1) -> list[str]:
    words = normalize_text(text).split()
    if n == 1:
        return words
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]


def compute_keyword_coverage(resume_text: str, jd_keywords: list[str]) -> dict:
    resume_lower = normalize_text(resume_text)
    matched, missing = [], []
    for kw in jd_keywords:
        kw_norm = normalize_text(kw)
        if kw_norm and kw_norm in resume_lower:
            matched.append(kw)
        else:
            missing.append(kw)

    coverage = (len(matched) / len(jd_keywords) * 100) if jd_keywords else 0
    return {
        "coverage_pct": round(coverage, 1),
        "matched": matched,
        "missing": missing,
        "total_keywords": len(jd_keywords),
        "matched_count": len(matched),
    }


def compute_ats_score(resume_text: str, jd_keywords: list[str], required_skills: list[str], preferred_skills: list[str]) -> dict:
    req_cov = compute_keyword_coverage(resume_text, required_skills)
    pref_cov = compute_keyword_coverage(resume_text, preferred_skills)
    kw_cov = compute_keyword_coverage(resume_text, jd_keywords)

    required_score = req_cov["coverage_pct"] * 0.60
    preferred_score = pref_cov["coverage_pct"] * 0.25
    keyword_score = kw_cov["coverage_pct"] * 0.15
    total = round(required_score + preferred_score + keyword_score, 1)

    return {
        "ats_score": min(total, 100),
        "required_skill_coverage": req_cov,
        "preferred_skill_coverage": pref_cov,
        "keyword_coverage": kw_cov,
        "breakdown": {
            "required_contribution": round(required_score, 1),
            "preferred_contribution": round(preferred_score, 1),
            "keyword_contribution": round(keyword_score, 1),
        }
    }


def detect_ats_issues(resume_text: str) -> list[str]:
    issues = []
    if len(resume_text) < 300:
        issues.append("Resume is too short — ATS may not extract enough content")
    if re.search(r"\btable\b|\bcell\b", resume_text, re.I):
        issues.append("Avoid tables — ATS parsers often misread them")
    if resume_text.count("|") > 10:
        issues.append("Excessive pipe characters detected — may confuse ATS")
    if not re.search(r"\b(experience|work)\b", resume_text, re.I):
        issues.append("Missing 'Experience' section heading")
    if not re.search(r"\b(education|degree|university|bachelor|master)\b", resume_text, re.I):
        issues.append("Missing 'Education' section heading")
    if len(re.findall(r"\b\d+%\b|\b\d+x\b|\b\$\d+", resume_text)) < 2:
        issues.append("Few quantified metrics found — add numbers/percentages to demonstrate impact")
    return issues


def detect_redundancy(text: str) -> list[str]:
    issues = []
    filler_phrases = [
        "responsible for", "duties include", "worked on", "helped with",
        "assisted in", "team player", "hard worker", "self-motivated",
        "detail-oriented", "go-getter", "passionate about", "synergy",
        "leveraged", "utilized", "facilitated the", "in order to"
    ]
    text_lower = text.lower()
    for phrase in filler_phrases:
        if phrase in text_lower:
            issues.append(f"Weak/filler phrase detected: '{phrase}'")

    sentences = [s.strip() for s in re.split(r"[.\n]", text) if len(s.strip()) > 20]
    seen = Counter()
    for s in sentences:
        key = " ".join(s.lower().split()[:5])
        seen[key] += 1
    for key, count in seen.items():
        if count > 1:
            issues.append(f"Repeated sentence start: '{key}...' appears {count} times")

    return issues[:10]
