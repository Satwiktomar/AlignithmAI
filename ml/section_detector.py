"""
Resume Section Detector — Identifies canonical ATS sections in resume text.

Detects: Contact, Summary/Objective, Experience, Education, Skills,
Projects, Certifications, Awards/Honors, Languages, Volunteer/Activities.
"""

import re
from dataclasses import dataclass, field


@dataclass
class SectionMatch:
    name: str
    found: bool
    confidence: float  # 0.0 – 1.0
    heading_text: str = ""
    start_pos: int = -1


# ── Canonical section patterns ──────────────────────────────────────────
# Each key is a canonical ATS section name.
# Values are compiled regex patterns that match common headings.

SECTION_PATTERNS: dict[str, re.Pattern] = {
    "Contact Information": re.compile(
        r"(?i)^\s*(?:contact\s*(?:info(?:rmation)?)?|personal\s*(?:info(?:rmation)?|details))\s*$",
        re.MULTILINE,
    ),
    "Summary": re.compile(
        r"(?i)^\s*(?:summary|professional\s*summary|executive\s*summary|profile|about\s*me|objective|career\s*objective)\s*$",
        re.MULTILINE,
    ),
    "Experience": re.compile(
        r"(?i)^\s*(?:(?:work|professional|relevant|employment)\s*)?(?:experience|history)\s*$",
        re.MULTILINE,
    ),
    "Education": re.compile(
        r"(?i)^\s*(?:education|academic\s*(?:background|qualifications)|degrees?)\s*$",
        re.MULTILINE,
    ),
    "Skills": re.compile(
        r"(?i)^\s*(?:(?:technical|core|key|relevant|professional)\s*)?skills?\s*(?:&\s*(?:tools|technologies|competencies))?\s*$",
        re.MULTILINE,
    ),
    "Projects": re.compile(
        r"(?i)^\s*(?:(?:personal|academic|relevant|key|selected)\s*)?projects?\s*$",
        re.MULTILINE,
    ),
    "Certifications": re.compile(
        r"(?i)^\s*(?:certifications?|licenses?\s*(?:&\s*certifications?)?|professional\s*certifications?)\s*$",
        re.MULTILINE,
    ),
    "Awards": re.compile(
        r"(?i)^\s*(?:awards?|honors?|achievements?|recognitions?)\s*(?:&\s*(?:honors?|awards?))?\s*$",
        re.MULTILINE,
    ),
    "Languages": re.compile(
        r"(?i)^\s*(?:languages?\s*(?:spoken|known)?)\s*$",
        re.MULTILINE,
    ),
    "Volunteer": re.compile(
        r"(?i)^\s*(?:volunteer(?:ing)?|community\s*(?:service|involvement)|extracurricular|activities)\s*$",
        re.MULTILINE,
    ),
}

# Sections that are *required* by most ATS parsers
ATS_REQUIRED_SECTIONS = {"Experience", "Education", "Skills"}

# Sections that are *recommended* for a strong resume
ATS_RECOMMENDED_SECTIONS = {"Summary", "Projects", "Certifications"}


def detect_sections(text: str) -> dict:
    """
    Detect canonical ATS sections in resume text.

    Returns:
        {
            "sections_found": [{"name": ..., "confidence": ..., "heading": ...}, ...],
            "sections_missing": [...],
            "required_found": [...],
            "required_missing": [...],
            "recommended_found": [...],
            "recommended_missing": [...],
            "section_score": 0-100,
        }
    """
    found: list[dict] = []
    missing: list[str] = []

    for section_name, pattern in SECTION_PATTERNS.items():
        match = pattern.search(text)
        if match:
            found.append({
                "name": section_name,
                "confidence": 1.0,
                "heading": match.group(0).strip(),
                "position": match.start(),
            })
        else:
            # Fallback: check if section content exists even without heading
            confidence = _infer_section_presence(section_name, text)
            if confidence >= 0.6:
                found.append({
                    "name": section_name,
                    "confidence": round(confidence, 2),
                    "heading": "(inferred)",
                    "position": -1,
                })
            else:
                missing.append(section_name)

    found_names = {s["name"] for s in found}
    req_found = sorted(ATS_REQUIRED_SECTIONS & found_names)
    req_missing = sorted(ATS_REQUIRED_SECTIONS - found_names)
    rec_found = sorted(ATS_RECOMMENDED_SECTIONS & found_names)
    rec_missing = sorted(ATS_RECOMMENDED_SECTIONS - found_names)

    # Section score: 60% required, 30% recommended, 10% extras
    req_pct = len(req_found) / len(ATS_REQUIRED_SECTIONS) if ATS_REQUIRED_SECTIONS else 1
    rec_pct = len(rec_found) / len(ATS_RECOMMENDED_SECTIONS) if ATS_RECOMMENDED_SECTIONS else 1
    extra_pct = max(0, len(found_names) - len(ATS_REQUIRED_SECTIONS) - len(ATS_RECOMMENDED_SECTIONS)) / 4
    section_score = round(min((req_pct * 60 + rec_pct * 30 + min(extra_pct, 1) * 10), 100), 1)

    return {
        "sections_found": sorted(found, key=lambda s: s.get("position", 9999)),
        "sections_missing": missing,
        "required_found": req_found,
        "required_missing": req_missing,
        "recommended_found": rec_found,
        "recommended_missing": rec_missing,
        "section_score": section_score,
    }


def _infer_section_presence(section_name: str, text: str) -> float:
    """Heuristic check for section content when no heading is found."""
    text_lower = text.lower()

    if section_name == "Contact Information":
        has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text))
        has_phone = bool(re.search(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text))
        return 0.9 if (has_email and has_phone) else 0.5 if has_email else 0.0

    if section_name == "Experience":
        date_ranges = len(re.findall(
            r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}\s*[-–—]\s*(?:present|\w+\s+\d{4})",
            text_lower,
        ))
        return min(date_ranges * 0.3, 1.0)

    if section_name == "Education":
        edu_words = sum(1 for w in ["bachelor", "master", "degree", "university", "college", "b.s.", "m.s.", "ph.d.", "gpa"]
                        if w in text_lower)
        return min(edu_words * 0.25, 1.0)

    if section_name == "Skills":
        # Check for comma-separated or bullet-listed skill patterns
        skill_lines = len(re.findall(r"(?:python|java|react|sql|docker|aws|git|node)", text_lower))
        return min(skill_lines * 0.15, 1.0)

    return 0.0
