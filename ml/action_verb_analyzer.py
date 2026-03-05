"""
Action Verb Analyzer — Scores resume bullet points for action verb strength.

Categorizes verbs as STRONG / MEDIUM / WEAK / PASSIVE and provides
replacement suggestions for weak/passive language.
"""

import re
from collections import Counter


# ── Action Verb Database ────────────────────────────────────────────────

STRONG_VERBS: set[str] = {
    # Leadership & Strategy
    "spearheaded", "orchestrated", "championed", "pioneered", "transformed",
    "revolutionized", "overhauled", "directed", "led", "drove",
    # Impact & Results
    "accelerated", "amplified", "boosted", "decreased", "delivered",
    "doubled", "eliminated", "exceeded", "generated", "improved",
    "increased", "maximized", "minimized", "optimized", "reduced",
    "saved", "streamlined", "tripled", "yielded",
    # Technical / Engineering
    "architected", "automated", "benchmarked", "containerized", "debugged",
    "deployed", "engineered", "integrated", "migrated", "modernized",
    "refactored", "scaled", "shipped", "instrumented",
    # Innovation
    "invented", "conceptualized", "devised", "formulated", "innovated",
    "prototyped", "redesigned", "reengineered",
    # Communication & Influence
    "advocated", "influenced", "mentored", "negotiated", "persuaded",
    "presented", "published", "trained",
}

MEDIUM_VERBS: set[str] = {
    "analyzed", "built", "configured", "coordinated", "created",
    "customized", "designed", "developed", "established", "executed",
    "expanded", "facilitated", "identified", "implemented", "initiated",
    "launched", "maintained", "managed", "monitored", "operated",
    "organized", "performed", "planned", "prepared", "produced",
    "programmed", "provided", "resolved", "reviewed", "scheduled",
    "secured", "supported", "tested", "updated", "upgraded",
    "utilized", "wrote", "conducted", "collaborated",
}

WEAK_PHRASES: list[str] = [
    "responsible for", "duties included", "worked on", "helped with",
    "assisted in", "assisted with", "participated in", "involved in",
    "was part of", "contributed to", "part of a team",
    "tasked with", "in charge of", "handled",
]

PASSIVE_PATTERN = re.compile(
    r"\b(?:was|were|been|being|is|are|got)\s+\w+(?:ed|en)\b", re.IGNORECASE
)

# ── Replacement suggestions for weak phrases ────────────────────────────

VERB_SUGGESTIONS: dict[str, list[str]] = {
    "responsible for": ["led", "managed", "directed", "oversaw"],
    "duties included": ["delivered", "executed", "performed"],
    "worked on": ["developed", "built", "engineered", "designed"],
    "helped with": ["contributed to", "supported", "enabled", "facilitated"],
    "assisted in": ["supported", "enabled", "facilitated", "collaborated on"],
    "assisted with": ["supported", "enabled", "facilitated"],
    "participated in": ["contributed to", "collaborated on", "engaged in"],
    "involved in": ["contributed to", "played a key role in", "drove"],
    "was part of": ["contributed to", "collaborated within", "served on"],
    "contributed to": ["advanced", "strengthened", "enhanced"],
    "part of a team": ["collaborated with a team to", "partnered with"],
    "tasked with": ["appointed to", "led", "owned"],
    "in charge of": ["managed", "directed", "oversaw", "owned"],
    "handled": ["managed", "processed", "resolved", "executed"],
}


def analyze_bullets(text: str) -> dict:
    """
    Analyze resume text for action verb quality.

    Returns:
        {
            "action_verb_score": 0-100,
            "strong_count": int,
            "medium_count": int,
            "weak_count": int,
            "passive_count": int,
            "total_bullets": int,
            "weak_phrases_found": [{"phrase": ..., "suggestions": [...]}, ...],
            "passive_instances": [...],
            "verb_distribution": {"strong": ..., "medium": ..., "weak": ..., "passive": ...},
            "top_verbs_used": [{"verb": ..., "count": ...}, ...],
        }
    """
    # Split into bullet-like lines
    lines = [
        line.strip()
        for line in re.split(r"[\n•●▪▸►\-\*]", text)
        if len(line.strip()) > 15
    ]

    strong_count = 0
    medium_count = 0
    weak_count = 0
    passive_count = 0
    verb_counter: Counter = Counter()
    weak_found: list[dict] = []
    passive_instances: list[str] = []

    for line in lines:
        line_lower = line.lower().strip()
        line_classified = False

        # Check for weak phrases first (higher priority)
        for phrase in WEAK_PHRASES:
            if phrase in line_lower:
                weak_count += 1
                weak_found.append({
                    "phrase": phrase,
                    "context": line[:120],
                    "suggestions": VERB_SUGGESTIONS.get(phrase, ["Use a strong action verb"]),
                })
                line_classified = True
                break

        if line_classified:
            continue

        # Check for passive voice
        passive_matches = PASSIVE_PATTERN.findall(line)
        if passive_matches:
            passive_count += 1
            passive_instances.append(line[:120])
            continue

        # Extract first word as potential action verb
        first_word = re.match(r"^([a-zA-Z]+)", line_lower)
        if first_word:
            verb = first_word.group(1)
            verb_counter[verb] += 1

            if verb in STRONG_VERBS:
                strong_count += 1
            elif verb in MEDIUM_VERBS:
                medium_count += 1
            # else: neutral — not penalized but not scored either

    total = max(strong_count + medium_count + weak_count + passive_count, 1)

    # Score: strong = full weight, medium = half, weak/passive = penalty
    raw_score = (
        (strong_count * 100 + medium_count * 60) / total
        - (weak_count * 15 + passive_count * 10)
    )
    action_verb_score = round(max(0, min(100, raw_score)), 1)

    # Top verbs used
    top_verbs = [
        {"verb": v, "count": c}
        for v, c in verb_counter.most_common(10)
    ]

    return {
        "action_verb_score": action_verb_score,
        "strong_count": strong_count,
        "medium_count": medium_count,
        "weak_count": weak_count,
        "passive_count": passive_count,
        "total_bullets": len(lines),
        "weak_phrases_found": weak_found[:10],
        "passive_instances": passive_instances[:5],
        "verb_distribution": {
            "strong_pct": round(strong_count / total * 100, 1),
            "medium_pct": round(medium_count / total * 100, 1),
            "weak_pct": round(weak_count / total * 100, 1),
            "passive_pct": round(passive_count / total * 100, 1),
        },
        "top_verbs_used": top_verbs,
    }


def get_strong_verb_suggestions(category: str = "all") -> list[str]:
    """Return a list of strong action verbs, optionally filtered by category."""
    if category == "all":
        return sorted(STRONG_VERBS)
    # Could be extended with category filtering
    return sorted(STRONG_VERBS)
