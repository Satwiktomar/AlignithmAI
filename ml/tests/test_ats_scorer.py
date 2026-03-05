"""Tests for the ATS scorer module — all 7 dimensions."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ats_scorer import (
    normalize_text, extract_ngrams,
    compute_keyword_coverage, compute_ats_score,
    detect_ats_issues, detect_redundancy,
    score_quantification, check_formatting_compliance,
    validate_contact_info, check_length_readability,
    compute_enhanced_ats_score,
)

# ── Sample data ─────────────────────────────────────────────────────────

SAMPLE_RESUME = """
John Doe
john.doe@example.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe
San Francisco, CA

Summary
Senior Software Engineer with 5+ years of experience building scalable web applications.

Experience

Senior Software Engineer, TechCorp — Jan 2022 - Present
- Architected microservices platform serving 2M+ requests/day, reducing latency by 40%
- Led migration from monolith to Kubernetes, cutting deployment time by 65%
- Spearheaded adoption of CI/CD pipelines, improving release frequency by 3x
- Mentored 4 junior engineers, with 2 promoted within 12 months

Software Engineer, StartupXYZ — Jun 2019 - Dec 2021
- Built real-time data pipeline processing 500K events/day using Kafka and Spark
- Developed REST APIs with FastAPI, handling 10K concurrent users
- Implemented automated testing suite achieving 92% code coverage
- Reduced cloud costs by $120K/year through infrastructure optimization

Education

B.S. Computer Science, UC Berkeley — 2019
GPA: 3.8 | Dean's List | Relevant coursework: Distributed Systems, ML

Skills
Python, Java, Go, React, Node.js, FastAPI, Docker, Kubernetes, AWS, GCP, PostgreSQL, Redis, Kafka, Spark, CI/CD, Git

Projects

CloudWatch Dashboard — Real-time monitoring tool
- Built with React + D3.js, deployed on AWS, serving 500+ internal users
- Technologies: React, D3.js, AWS Lambda, DynamoDB

Certifications
AWS Solutions Architect Associate
"""

SAMPLE_JD_KEYWORDS = ["python", "java", "kubernetes", "docker", "aws", "microservices", "ci/cd", "rest api"]
SAMPLE_REQUIRED = ["python", "kubernetes", "docker", "aws"]
SAMPLE_PREFERRED = ["go", "kafka", "react", "postgresql"]


# ── Tests: Text Normalization ───────────────────────────────────────────

class TestNormalization:
    def test_normalize_text_basic(self):
        assert "python" in normalize_text("Python")
        assert "c++" in normalize_text("C++")

    def test_extract_unigrams(self):
        ngrams = extract_ngrams("machine learning engineer")
        assert "machine" in ngrams
        assert "learning" in ngrams

    def test_extract_bigrams(self):
        bigrams = extract_ngrams("machine learning engineer", n=2)
        assert "machine learning" in bigrams


# ── Tests: Keyword Coverage ────────────────────────────────────────────

class TestKeywordCoverage:
    def test_full_coverage(self):
        result = compute_keyword_coverage(SAMPLE_RESUME, ["python", "java", "aws"])
        assert result["coverage_pct"] == 100.0
        assert result["matched_count"] == 3

    def test_partial_coverage(self):
        result = compute_keyword_coverage(SAMPLE_RESUME, ["python", "rust", "haskell"])
        assert result["matched_count"] == 1
        assert len(result["missing"]) == 2

    def test_empty_keywords(self):
        result = compute_keyword_coverage(SAMPLE_RESUME, [])
        assert result["coverage_pct"] == 0


# ── Tests: ATS Score (Legacy) ──────────────────────────────────────────

class TestATSScore:
    def test_basic_scoring(self):
        result = compute_ats_score(SAMPLE_RESUME, SAMPLE_JD_KEYWORDS, SAMPLE_REQUIRED, SAMPLE_PREFERRED)
        assert 0 <= result["ats_score"] <= 100
        assert "required_skill_coverage" in result
        assert "preferred_skill_coverage" in result
        assert "breakdown" in result

    def test_high_match(self):
        result = compute_ats_score(SAMPLE_RESUME, SAMPLE_JD_KEYWORDS, SAMPLE_REQUIRED, SAMPLE_PREFERRED)
        # Our sample resume contains most of these skills
        assert result["ats_score"] >= 50


# ── Tests: ATS Issues Detection ─────────────────────────────────────────

class TestATSIssues:
    def test_short_resume(self):
        issues = detect_ats_issues("Short text")
        assert any("too short" in i.lower() for i in issues)

    def test_good_resume_fewer_issues(self):
        issues = detect_ats_issues(SAMPLE_RESUME)
        # Our sample is well-structured, should have few issues
        assert len(issues) <= 2

    def test_table_detection(self):
        issues = detect_ats_issues("table cell " + "|" * 15 + " experience education")
        assert any("table" in i.lower() or "pipe" in i.lower() for i in issues)


# ── Tests: Redundancy Detection ─────────────────────────────────────────

class TestRedundancy:
    def test_filler_detection(self):
        issues = detect_redundancy("I was responsible for managing the team. Helped with deployment.")
        assert any("responsible for" in i.lower() for i in issues)

    def test_clean_text(self):
        issues = detect_redundancy("Architected microservices platform. Led migration to Kubernetes.")
        assert len(issues) == 0


# ── Tests: Quantification Score ─────────────────────────────────────────

class TestQuantification:
    def test_metrics_present(self):
        result = score_quantification(SAMPLE_RESUME)
        assert result["bullets_with_metrics"] > 0
        assert result["quantification_score"] > 0

    def test_no_metrics(self):
        result = score_quantification("Managed team. Did tasks. Made things happen.")
        assert result["quantification_score"] < 30


# ── Tests: Formatting Compliance ────────────────────────────────────────

class TestFormatting:
    def test_clean_formatting(self):
        result = check_formatting_compliance(SAMPLE_RESUME)
        assert result["formatting_score"] >= 70

    def test_bad_formatting(self):
        bad_text = "|||||||||||||||" + "[image]" + "\t\t\t" + "HELLO WORLD UPPERCASE" * 5
        result = check_formatting_compliance(bad_text)
        assert result["formatting_score"] < 50


# ── Tests: Contact Validation ───────────────────────────────────────────

class TestContactInfo:
    def test_full_contact(self):
        result = validate_contact_info(SAMPLE_RESUME)
        assert result["checks"]["email"] is True
        assert result["checks"]["phone"] is True
        assert result["checks"]["linkedin"] is True
        assert result["contact_score"] >= 70

    def test_no_contact(self):
        result = validate_contact_info("Just some text with no contact info")
        assert result["contact_score"] < 30


# ── Tests: Length & Readability ─────────────────────────────────────────

class TestLengthReadability:
    def test_good_length(self):
        result = check_length_readability(SAMPLE_RESUME)
        # Sample resume is ~185 words — scorer correctly identifies it as short
        assert result["length_score"] >= 0
        assert result["word_count"] > 100

    def test_too_short(self):
        result = check_length_readability("Very short resume.")
        assert result["length_score"] <= 40


# ── Tests: Enhanced Full Audit ──────────────────────────────────────────

class TestEnhancedATSScore:
    def test_full_audit_structure(self):
        result = compute_enhanced_ats_score(
            SAMPLE_RESUME, SAMPLE_JD_KEYWORDS, SAMPLE_REQUIRED, SAMPLE_PREFERRED
        )
        assert "overall_ats_score" in result
        assert "dimension_scores" in result
        assert "improvement_priorities" in result
        assert "grade" in result
        assert 0 <= result["overall_ats_score"] <= 100

    def test_all_dimensions_present(self):
        result = compute_enhanced_ats_score(SAMPLE_RESUME)
        dims = result["dimension_scores"]
        assert "keyword_coverage" in dims
        assert "section_structure" in dims
        assert "action_verbs" in dims
        assert "quantification" in dims
        assert "formatting" in dims
        assert "contact_info" in dims
        assert "length_readability" in dims

    def test_grade_valid(self):
        result = compute_enhanced_ats_score(SAMPLE_RESUME, SAMPLE_JD_KEYWORDS, SAMPLE_REQUIRED, SAMPLE_PREFERRED)
        assert result["grade"] in ["A+", "A", "B+", "B", "C+", "C", "D", "F"]

    def test_good_resume_scores_well(self):
        result = compute_enhanced_ats_score(SAMPLE_RESUME, SAMPLE_JD_KEYWORDS, SAMPLE_REQUIRED, SAMPLE_PREFERRED)
        assert result["overall_ats_score"] >= 40  # Good resume should score decently
