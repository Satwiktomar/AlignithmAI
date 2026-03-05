"""
ATS Scorer — Multi-dimensional Applicant Tracking System analysis.

Provides 7-dimension ATS scoring:
  1. Keyword Coverage (required / preferred / general)
  2. Section Detection
  3. Action Verb Quality
  4. Quantification Score
  5. Formatting Compliance
  6. Contact Information Validation
  7. Length & Readability
"""

import re
from collections import Counter
from typing import Optional

from section_detector import detect_sections
from action_verb_analyzer import analyze_bullets


# ── Text Normalization ──────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\s+#.]", " ", text.lower())


def extract_ngrams(text: str, n: int = 1) -> list[str]:
    words = normalize_text(text).split()
    if n == 1:
        return words
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]


# ── 1. Keyword Coverage ────────────────────────────────────────────────

def compute_keyword_coverage(resume_text: str, jd_keywords: list[str]) -> dict:
    resume_lower = normalize_text(resume_text)
    # Use bigram matching as well for multi-word keywords
    resume_bigrams = set(extract_ngrams(resume_text, 2))

    matched, missing = [], []
    for kw in jd_keywords:
        kw_norm = normalize_text(kw).strip()
        if not kw_norm:
            continue
        if kw_norm in resume_lower or kw_norm in resume_bigrams:
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


# ── 2. Section Detection (delegated) ───────────────────────────────────

# Uses section_detector.detect_sections() directly


# ── 3. Action Verb Quality (delegated) ──────────────────────────────────

# Uses action_verb_analyzer.analyze_bullets() directly


# ── 4. Quantification Score ─────────────────────────────────────────────

def score_quantification(text: str) -> dict:
    """Score the presence of metrics/numbers/percentages in bullet points."""
    lines = [
        line.strip()
        for line in re.split(r"[\n•●▪▸►\-\*]", text)
        if len(line.strip()) > 15
    ]

    metric_patterns = [
        r"\d+%",           # percentages
        r"\$[\d,.]+[KMBkmb]?",  # dollar amounts
        r"\d+x\b",         # multipliers
        r"\d{1,3}(?:,\d{3})+",  # large numbers with commas
        r"\b\d+\+?\s*(?:users?|customers?|clients?|employees?|requests?|transactions?|records?|projects?|teams?|people|members?)\b",
        r"\b(?:reduced|increased|improved|grew|saved|cut|boosted|decreased)\s+(?:by\s+)?\d+",
    ]

    bullets_with_metrics = 0
    metric_examples: list[str] = []

    for line in lines:
        for pattern in metric_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                bullets_with_metrics += 1
                metric_examples.append(line[:100])
                break

    total = max(len(lines), 1)
    # Ideal: at least 60% of bullets have metrics
    raw_score = min((bullets_with_metrics / total) / 0.6 * 100, 100)

    return {
        "quantification_score": round(raw_score, 1),
        "bullets_with_metrics": bullets_with_metrics,
        "total_bullets": len(lines),
        "metric_pct": round(bullets_with_metrics / total * 100, 1),
        "examples": metric_examples[:5],
        "tip": (
            "Great use of metrics!" if raw_score >= 80
            else "Add numbers, percentages, or dollar amounts to more bullet points"
            if raw_score >= 40
            else "Most bullets lack quantified impact — add metrics to demonstrate results"
        ),
    }


# ── 5. Formatting Compliance ────────────────────────────────────────────

def check_formatting_compliance(text: str) -> dict:
    """Detect ATS-hostile formatting patterns."""
    issues: list[str] = []

    # Tables
    if text.count("|") > 10:
        issues.append("Excessive pipe characters — likely table formatting that ATS parsers misread")
    if re.search(r"\btable\b|\bcell\b", text, re.IGNORECASE):
        issues.append("Table-related keywords detected — ATS may not parse tabular layouts")

    # Headers/Footers markers
    if re.search(r"page\s+\d+\s+of\s+\d+", text, re.IGNORECASE):
        issues.append("Page number detected — may indicate header/footer content bleeding into text")

    # Graphics/image markers
    if re.search(r"\[image\]|\[graphic\]|\[chart\]|\[logo\]", text, re.IGNORECASE):
        issues.append("Image/graphic marker found — ATS cannot parse visual elements")

    # Special Unicode characters
    unicode_chars = len(re.findall(r"[^\x00-\x7F]", text))
    if unicode_chars > 20:
        issues.append(f"High count of special/Unicode characters ({unicode_chars}) — may cause parsing errors")

    # Multi-column indicators
    if re.search(r"\t{2,}", text):
        issues.append("Multiple tab characters suggest column layout — ATS may misread order")

    # All-caps sections (more than 3 consecutive all-caps words)
    if len(re.findall(r"\b[A-Z]{4,}\b", text)) > 5:
        issues.append("Excessive ALL-CAPS text — use standard capitalization for ATS compatibility")

    # Unusual bullet characters
    unusual_bullets = len(re.findall(r"[◆◇★☆✦✧❖⬥⬦]", text))
    if unusual_bullets > 3:
        issues.append("Unusual bullet characters detected — use standard bullets (•, -, *)")

    # Score: start at 100, deduct per issue
    score = max(0, 100 - len(issues) * 15)

    return {
        "formatting_score": score,
        "issues": issues,
        "issue_count": len(issues),
        "verdict": (
            "✅ Clean formatting — ATS-friendly" if score >= 80
            else "⚠️ Some formatting concerns — review flagged items" if score >= 50
            else "❌ Significant formatting issues — may cause ATS parsing failures"
        ),
    }


# ── 6. Contact Information Validation ───────────────────────────────────

def validate_contact_info(text: str) -> dict:
    """Check for presence of essential contact information."""
    checks = {
        "email": bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)),
        "phone": bool(re.search(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text)),
        "linkedin": bool(re.search(r"linkedin\.com/in/[\w-]+", text, re.IGNORECASE)),
        "github": bool(re.search(r"github\.com/[\w-]+", text, re.IGNORECASE)),
        "portfolio": bool(re.search(r"(?:portfolio|website|blog)[\s:]*(?:https?://)?[\w.-]+\.\w+", text, re.IGNORECASE)),
        "location": bool(re.search(
            r"\b(?:[A-Z][a-z]+(?:\s[A-Z][a-z]+)?,\s*[A-Z]{2})\b"  # "City, ST" pattern
            r"|(?:remote|hybrid|on-site)",
            text, re.IGNORECASE
        )),
    }

    essential = ["email", "phone"]
    recommended = ["linkedin", "location"]

    essential_found = sum(1 for k in essential if checks[k])
    recommended_found = sum(1 for k in recommended if checks[k])

    score = round(
        (essential_found / len(essential)) * 70 +
        (recommended_found / len(recommended)) * 30,
        1,
    )

    missing = [k for k, v in checks.items() if not v and k in essential + recommended]

    return {
        "contact_score": score,
        "checks": checks,
        "missing_essential": [k for k in essential if not checks[k]],
        "missing_recommended": [k for k in recommended if not checks[k]],
        "missing": missing,
    }


# ── 7. Length & Readability ─────────────────────────────────────────────

def check_length_readability(text: str) -> dict:
    """Check resume length and basic readability metrics."""
    words = text.split()
    word_count = len(words)
    sentences = [s.strip() for s in re.split(r"[.!?]", text) if len(s.strip()) > 5]
    avg_sentence_length = round(word_count / max(len(sentences), 1), 1)

    # Ideal resume: 400-800 words for 1 page, 600-1200 for 2 pages
    if word_count < 200:
        length_verdict = "Too short — ATS may flag as incomplete"
        length_score = 30
    elif word_count < 400:
        length_verdict = "Short — consider adding more detail"
        length_score = 60
    elif word_count <= 900:
        length_verdict = "Good length for a 1-page resume"
        length_score = 100
    elif word_count <= 1400:
        length_verdict = "Appropriate for a 2-page resume"
        length_score = 90
    else:
        length_verdict = "Very long — consider trimming to 1-2 pages"
        length_score = 60

    # Readability: penalize very long or very short sentences
    if avg_sentence_length > 30:
        readability_note = "Sentences are too long — aim for 15-25 words"
        length_score = max(length_score - 15, 0)
    elif avg_sentence_length < 8:
        readability_note = "Sentences are very short — may lack detail"
        length_score = max(length_score - 10, 0)
    else:
        readability_note = "Good sentence length"

    return {
        "length_score": length_score,
        "word_count": word_count,
        "sentence_count": len(sentences),
        "avg_sentence_length": avg_sentence_length,
        "length_verdict": length_verdict,
        "readability_note": readability_note,
    }


# ── Legacy: ATS Issues + Redundancy (kept for backward compat) ──────────

def detect_ats_issues(resume_text: str) -> list[str]:
    """Legacy function — returns a flat list of ATS issues."""
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


# ── Legacy: Basic ATS Score (kept for backward compat) ──────────────────

def compute_ats_score(
    resume_text: str,
    jd_keywords: list[str],
    required_skills: list[str],
    preferred_skills: list[str],
) -> dict:
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
        },
    }


# ── Enhanced: Full 7-Dimension ATS Audit ────────────────────────────────

def compute_enhanced_ats_score(
    resume_text: str,
    jd_keywords: list[str] | None = None,
    required_skills: list[str] | None = None,
    preferred_skills: list[str] | None = None,
) -> dict:
    """
    Full 7-dimension ATS audit.

    Weights:
      - Keyword Coverage:     25%
      - Section Detection:    20%
      - Action Verbs:         15%
      - Quantification:       15%
      - Formatting:           10%
      - Contact Info:         10%
      - Length/Readability:     5%
    """
    jd_keywords = jd_keywords or []
    required_skills = required_skills or []
    preferred_skills = preferred_skills or []

    # 1. Keyword Coverage
    kw_result = compute_ats_score(resume_text, jd_keywords, required_skills, preferred_skills)
    kw_score = kw_result["ats_score"]

    # 2. Section Detection
    section_result = detect_sections(resume_text)
    section_score = section_result["section_score"]

    # 3. Action Verb Quality
    verb_result = analyze_bullets(resume_text)
    verb_score = verb_result["action_verb_score"]

    # 4. Quantification
    quant_result = score_quantification(resume_text)
    quant_score = quant_result["quantification_score"]

    # 5. Formatting Compliance
    format_result = check_formatting_compliance(resume_text)
    format_score = format_result["formatting_score"]

    # 6. Contact Information
    contact_result = validate_contact_info(resume_text)
    contact_score = contact_result["contact_score"]

    # 7. Length & Readability
    length_result = check_length_readability(resume_text)
    length_score = length_result["length_score"]

    # Weighted overall score
    overall = round(
        kw_score * 0.25 +
        section_score * 0.20 +
        verb_score * 0.15 +
        quant_score * 0.15 +
        format_score * 0.10 +
        contact_score * 0.10 +
        length_score * 0.05,
        1,
    )

    # Generate prioritized improvements
    dimensions = [
        ("Keyword Coverage", kw_score, "Add missing required skills and JD keywords to your resume"),
        ("Section Structure", section_score, f"Add missing sections: {', '.join(section_result.get('required_missing', []))}"),
        ("Action Verbs", verb_score, "Replace weak phrases with strong action verbs (led, architected, optimized)"),
        ("Quantification", quant_score, "Add metrics, percentages, and numbers to more bullet points"),
        ("Formatting", format_score, "Fix formatting issues for better ATS parsability"),
        ("Contact Info", contact_score, f"Add missing: {', '.join(contact_result.get('missing', []))}"),
        ("Length", length_score, length_result["length_verdict"]),
    ]
    priorities = sorted(
        [{"dimension": d, "score": s, "action": a} for d, s, a in dimensions if s < 80],
        key=lambda x: x["score"],
    )

    return {
        "overall_ats_score": overall,
        "dimension_scores": {
            "keyword_coverage": kw_score,
            "section_structure": section_score,
            "action_verbs": verb_score,
            "quantification": quant_score,
            "formatting": format_score,
            "contact_info": contact_score,
            "length_readability": length_score,
        },
        "keyword_details": kw_result,
        "section_details": section_result,
        "action_verb_details": verb_result,
        "quantification_details": quant_result,
        "formatting_details": format_result,
        "contact_details": contact_result,
        "length_details": length_result,
        "improvement_priorities": priorities[:5],
        "grade": (
            "A+" if overall >= 90 else
            "A" if overall >= 80 else
            "B+" if overall >= 70 else
            "B" if overall >= 60 else
            "C+" if overall >= 50 else
            "C" if overall >= 40 else
            "D" if overall >= 30 else "F"
        ),
    }
