"""Tests for skill taxonomy, section detection, and action verb analysis."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skill_taxonomy import normalize_skill, normalize_skills, find_skill_overlap, get_taxonomy_stats
from section_detector import detect_sections
from action_verb_analyzer import analyze_bullets, get_strong_verb_suggestions


# ── Skill Taxonomy Tests ────────────────────────────────────────────────

class TestSkillNormalization:
    def test_exact_match(self):
        assert normalize_skill("Python") == "Python"
        assert normalize_skill("python") == "Python"

    def test_alias_resolution(self):
        assert normalize_skill("js") == "JavaScript"
        assert normalize_skill("k8s") == "Kubernetes"
        assert normalize_skill("react.js") == "React"
        assert normalize_skill("pytorch") == "PyTorch"
        assert normalize_skill("tf") == "TensorFlow"

    def test_new_taxonomy_entries(self):
        assert normalize_skill("dbt") == "dbt"
        assert normalize_skill("snowflake") == "Snowflake"
        assert normalize_skill("kafka") == "Kafka"
        assert normalize_skill("helm") == "Helm"
        assert normalize_skill("tailwind") == "Tailwind CSS"

    def test_unknown_skill_passthrough(self):
        assert normalize_skill("SuperObscureFramework") == "SuperObscureFramework"

    def test_normalize_skills_dedup(self):
        result = normalize_skills(["python", "Python", "py", "js", "JavaScript"])
        assert len(result) == 2
        assert "Python" in result
        assert "JavaScript" in result


class TestSkillOverlap:
    def test_perfect_overlap(self):
        result = find_skill_overlap(["python", "react"], ["Python", "React"])
        assert result["coverage_pct"] == 100.0

    def test_partial_overlap(self):
        result = find_skill_overlap(["python", "react"], ["Python", "Go", "Rust"])
        assert result["matched_count"] == 1
        assert len(result["missing"]) == 2

    def test_alias_matching(self):
        result = find_skill_overlap(["js", "k8s"], ["JavaScript", "Kubernetes"])
        assert result["coverage_pct"] == 100.0


class TestTaxonomyStats:
    def test_stats_structure(self):
        stats = get_taxonomy_stats()
        assert stats["total_skills"] >= 150
        assert "categories" in stats


# ── Section Detector Tests ──────────────────────────────────────────────

SAMPLE_RESUME_WITH_SECTIONS = """
Contact Information
John Doe | john@example.com | (555) 123-4567

Summary
Experienced software engineer with 5+ years.

Experience
Senior Engineer at TechCorp — 2022-Present

Education
BS Computer Science, MIT — 2018

Skills
Python, Java, Docker, Kubernetes

Projects
CloudWatch Dashboard — monitoring tool

Certifications
AWS Solutions Architect
"""


class TestSectionDetector:
    def test_finds_all_sections(self):
        result = detect_sections(SAMPLE_RESUME_WITH_SECTIONS)
        found_names = {s["name"] for s in result["sections_found"]}
        assert "Experience" in found_names
        assert "Education" in found_names
        assert "Skills" in found_names

    def test_required_sections(self):
        result = detect_sections(SAMPLE_RESUME_WITH_SECTIONS)
        assert len(result["required_missing"]) == 0

    def test_section_score_range(self):
        result = detect_sections(SAMPLE_RESUME_WITH_SECTIONS)
        assert 0 <= result["section_score"] <= 100

    def test_missing_sections_detected(self):
        result = detect_sections("Just some random text with no structure")
        assert len(result["sections_missing"]) > 0


# ── Action Verb Analyzer Tests ──────────────────────────────────────────

class TestActionVerbAnalyzer:
    def test_strong_verbs_detected(self):
        text = """
        - Architected microservices platform
        - Spearheaded migration to cloud
        - Optimized database queries reducing latency by 40%
        """
        result = analyze_bullets(text)
        assert result["strong_count"] >= 2
        assert result["action_verb_score"] > 50

    def test_weak_phrases_detected(self):
        text = """
        - Responsible for managing the team
        - Helped with deployment issues
        - Worked on various projects
        """
        result = analyze_bullets(text)
        assert result["weak_count"] >= 2
        assert len(result["weak_phrases_found"]) >= 2

    def test_suggestions_provided(self):
        text = "Responsible for managing the backend services"
        result = analyze_bullets(text)
        if result["weak_phrases_found"]:
            assert len(result["weak_phrases_found"][0]["suggestions"]) > 0

    def test_score_range(self):
        result = analyze_bullets("Architected amazing system. Led team. Optimized everything.")
        assert 0 <= result["action_verb_score"] <= 100

    def test_strong_verb_list(self):
        verbs = get_strong_verb_suggestions()
        assert len(verbs) >= 50
        assert "architected" in verbs
        assert "spearheaded" in verbs
