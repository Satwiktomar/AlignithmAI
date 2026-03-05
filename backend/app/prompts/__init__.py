RESUME_PARSE_PROMPT = """
You are a professional resume parser optimized for ATS (Applicant Tracking System) extraction. Extract ALL information from the resume text below into a structured JSON format.
Today's date: {current_date}

RESUME TEXT:
{resume_text}

Return ONLY a valid JSON object with this exact structure:
{{
  "name": "",
  "email": "",
  "phone": "",
  "location": "",
  "linkedin": "",
  "github": "",
  "portfolio": "",
  "current_title": "",
  "summary": "",
  "total_experience_years": 0,
  "skills": {{
    "technical": [],
    "soft": [],
    "tools": [],
    "languages": [],
    "frameworks": [],
    "databases": [],
    "cloud": [],
    "devops": [],
    "certifications": []
  }},
  "experience": [
    {{
      "title": "",
      "company": "",
      "location": "",
      "start_date": "",
      "end_date": "",
      "duration": "",
      "is_current": false,
      "bullets": [],
      "metrics": [],
      "action_verbs": []
    }}
  ],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "location": "",
      "graduation_date": "",
      "gpa": "",
      "relevant_courses": [],
      "honors": []
    }}
  ],
  "projects": [
    {{
      "title": "",
      "description": "",
      "technologies": [],
      "metrics": [],
      "github_url": "",
      "bullets": []
    }}
  ],
  "certifications": [],
  "awards": [],
  "languages_spoken": [],
  "sections_detected": [],
  "ats_notes": {{
    "has_contact_info": true,
    "has_summary": true,
    "has_experience": true,
    "has_education": true,
    "has_skills": true,
    "has_projects": true,
    "formatting_clean": true
  }}
}}

IMPORTANT:
- Parse the FULL resume. Do not truncate experience or projects.
- Mark is_current=true for roles with no end date or "Present".
- Extract ALL skills into appropriate categories (technical, tools, frameworks, databases, cloud, devops).
- For each experience bullet, identify the leading action verb and any quantified metrics.
- In sections_detected, list all section headings found in the resume.
- In ats_notes, flag which standard sections are present/missing.
"""


JD_PARSE_PROMPT = """
You are a job description analyst specializing in ATS keyword extraction. Extract ALL structured information from this job description, paying special attention to skills categorization and ATS-critical keywords.

JOB DESCRIPTION:
{jd_text}

Return ONLY a valid JSON object:
{{
  "job_title": "",
  "company": "",
  "location": "",
  "employment_type": "",
  "seniority_level": "",
  "experience_required": "",
  "required_skills": [],
  "preferred_skills": [],
  "technical_skills": [],
  "soft_skills": [],
  "tools_and_technologies": [],
  "responsibilities": [],
  "keywords": [],
  "qualifications": [],
  "nice_to_have": [],
  "industry": "",
  "domain": "",
  "ats_keywords": [],
  "skill_categories": {{
    "must_have": [],
    "strong_preference": [],
    "nice_to_have": []
  }},
  "experience_keywords": [],
  "action_verbs_expected": []
}}

IMPORTANT:
- ats_keywords should be the top 15-20 most important terms an ATS would scan for.
- Separate must_have vs strong_preference vs nice_to_have skills clearly.
- Extract action verbs the JD uses (e.g., "design", "build", "lead") — these indicate what the employer values.
"""


MATCH_ENGINE_PROMPT = """
You are an expert ATS (Applicant Tracking System) and career match analyst. Perform a comprehensive multi-dimensional analysis of the match between this resume and job description.

PARSED RESUME JSON:
{resume_json}

PARSED JD JSON:
{jd_json}

Compute scores across SEVEN dimensions and return ONLY a valid JSON:
{{
  "overall_score": 0,
  "skill_score": 0,
  "keyword_score": 0,
  "experience_score": 0,
  "ats_score": 0,
  "matched_skills": [],
  "missing_skills": [],
  "missing_critical_skills": [],
  "missing_preferred_skills": [],
  "matched_keywords": [],
  "missing_keywords": [],
  "experience_fit": "",
  "seniority_match": "",
  "strengths": [],
  "weaknesses": [],
  "ats_compliance": {{
    "section_completeness": 0,
    "keyword_density": 0,
    "action_verb_quality": 0,
    "quantification_level": 0,
    "formatting_safety": 0,
    "overall_ats_readiness": 0,
    "issues": [],
    "recommendations": []
  }},
  "ats_issues": [],
  "improvement_priority": [
    {{
      "area": "",
      "current_score": 0,
      "impact": "high|medium|low",
      "action": ""
    }}
  ],
  "keyword_optimization": {{
    "keywords_to_add": [],
    "keywords_well_placed": [],
    "keyword_density_assessment": ""
  }},
  "summary": ""
}}

SCORING RULES:
- All scores must be integers 0-100.
- skill_score: Weight required skills at 2x vs preferred skills.
- keyword_score: Measure how many JD keywords appear naturally in the resume.
- experience_score: Consider years, relevance, progression, and domain alignment.
- ats_score: Evaluate section structure, keyword presence, formatting, quantification, and action verb quality.
- ats_compliance should assess each sub-dimension independently.
- improvement_priority should list the top 5 actions that would most improve the match, ranked by impact.
- Be precise, specific, and actionable. Never give generic advice.
"""


COVER_LETTER_PROMPT = """
You are an expert career coach who writes exceptional, HUMAN cover letters that are optimized for both human readers and ATS systems.

STRICT RULES:
- NEVER use these phrases: "I am excited to apply", "I am passionate about", "I would be a great fit", "Looking forward to", "Thank you for your consideration", "dynamic team", "synergy", "leverage my skills"
- NO AI-sounding phrases
- Sound like a thoughtful, accomplished human professional
- Use specific evidence from the resume only (NO hallucination)
- Include 2-3 specific job requirements and how you meet them
- Include quantified achievements
- Be concise (under 350 words)

ATS OPTIMIZATION:
- Naturally incorporate 5-7 of the most important JD keywords into the letter
- Do NOT keyword-stuff — weave keywords into genuine, contextual sentences
- Use the exact job title from the JD at least once
- Mirror the language and terminology used in the JD

TONE: {tone}
(formal=professional and precise | semi-formal=warm and professional | startup=direct and energetic | direct=straight to the point | corporate=polished and formal)

APPLICANT RESUME (use ONLY this data):
{resume_json}

JOB DESCRIPTION:
{jd_json}

Write a complete cover letter. Start with "Dear Hiring Manager," unless you have the hiring manager's name.
Return ONLY the cover letter text, no JSON.
"""


RESUME_SUGGEST_PROMPT = """
You are a professional resume reviewer, career coach, and ATS optimization specialist. Analyze each resume bullet and provide specific improvements.

RESUME JSON:
{resume_json}

JOB DESCRIPTION KEYWORDS & SKILLS:
{jd_keywords}

For each bullet in experience and projects, provide ATS-optimized improvements. Return ONLY valid JSON:
{{
  "suggestions": [
    {{
      "section": "Experience | Project",
      "company_or_project": "",
      "original_bullet": "",
      "improved_bullet": "",
      "action_verb_change": {{"from": "", "to": ""}},
      "metric_suggestion": "",
      "keywords_added": [],
      "conciseness_improvement": "",
      "ats_optimization": "",
      "impact_level": "high|medium|low"
    }}
  ],
  "overall_recommendations": [],
  "top_action_verbs_to_use": [],
  "missing_sections": [],
  "keyword_placement_tips": [],
  "ats_formatting_fixes": []
}}

RULES:
- Only suggest improvements based on what is likely true. Never invent experience.
- Prioritize suggestions by impact_level — "high" for changes that would most improve ATS score.
- For action_verb_change, suggest strong action verbs: architected, spearheaded, optimized, reduced, increased, launched.
- For metric_suggestion, suggest realistic quantification (percentages, user counts, time saved).
- keyword_placement_tips should advise where to place missing JD keywords naturally.
- ats_formatting_fixes should flag any formatting issues (tables, graphics, unusual characters).
"""


PROJECT_RANK_PROMPT = """
You are an expert technical recruiter. Rank and evaluate these projects for relevance to the job description.

USER PROJECTS:
{projects_json}

JOB DESCRIPTION:
{jd_json}

Return ONLY valid JSON:
{{
  "ranked": [
    {{
      "id": 0,
      "title": "",
      "score": 0,
      "reason": "",
      "recommended": true,
      "keywords_to_add": [],
      "rank": 1
    }}
  ],
  "top_recommended": [],
  "missing_project_types": [],
  "summary": ""
}}

Score 0-100 for relevance. Rank all projects from most to least relevant.
"""


RECRUITER_SIM_PROMPT = """
You are a senior technical recruiter at a top tech company reviewing this resume for the given job.
Today's date: {current_date}

IMPORTANT: Use today's date as the reference for all time calculations. If an experience entry has no end date or says "Present", it is currently ongoing as of today. Do NOT treat future-looking dates as if they are hypothetical — if someone worked at Company X from Jan 2024 to Jan 2025, that is past experience, not future.

Simulate your honest first-impression reaction after a 30-second scan, then detailed review.

RESUME:
{resume_json}

TARGET JOB:
{jd_json}

Return ONLY valid JSON:
{{
  "first_impression": "",
  "shortlist_decision": "Shortlist" or "Do Not Shortlist",
  "technical_score": 0,
  "experience_score": 0,
  "culture_score": 0,
  "ats_readiness_score": 0,
  "strengths": [],
  "red_flags": [],
  "missing_elements": [],
  "formatting_notes": [],
  "advice": [],
  "keyword_gaps": [],
  "verdict": ""
}}

Scores 0-100. Be honest, specific, actionable. Never flag past/completed internships as future-dated.
Include ats_readiness_score — how well would this resume pass through an ATS before reaching your desk.
Include keyword_gaps — critical JD keywords missing from the resume.
"""


SKILL_GAP_PROMPT = """
You are a career development advisor and skills strategist. Based on the match analysis, create a comprehensive, actionable skill gap report with a detailed learning roadmap.
Today's date: {current_date}

MATCH DETAILS:
{match_json}

RESUME SKILLS:
{resume_skills}

JOB REQUIRED SKILLS:
{jd_skills}

Return ONLY valid JSON with these exact keys:
{{
  "missing_skills": [],
  "matched_skills": [],
  "skill_gap_severity": "low|medium|high|critical",
  "learning_roadmap": [
    {{
      "skill": "",
      "priority": "critical|high|medium|low",
      "category": "language|framework|tool|concept|cloud|database|devops|soft_skill",
      "action": "Concise what-to-do description",
      "why_needed": "One sentence on why the job requires this",
      "prerequisites": [
        {{
          "name": "",
          "description": "Brief explanation of why this prerequisite is needed",
          "already_known": false
        }}
      ],
      "resources": [
        {{
          "title": "",
          "url": "",
          "type": "course|docs|tutorial|book|project"
        }}
      ],
      "timeline": "",
      "estimated_hours": 0,
      "proficiency_target": "beginner|intermediate|advanced"
    }}
  ],
  "certifications": [
    {{
      "name": "",
      "provider": "",
      "url": "",
      "priority": "high|medium|low",
      "timeline": "",
      "covers_skills": []
    }}
  ],
  "quick_wins": [],
  "long_term_goals": [],
  "resume_update_tips": []
}}

RULES:
- Be specific and actionable. List concrete skills to acquire targeting the exact job requirements.
- Prioritize learning_roadmap items by priority (critical first).
- For EACH skill, list its prerequisites — foundational skills the learner needs first. If the user already has a prerequisite from their resume, set already_known=true.
- Include 1-3 real, accessible learning resources with actual URLs (official docs, freeCodeCamp, Coursera, YouTube, etc.).
- Include realistic estimated_hours for each skill.
- certifications must be REAL, verifiable certifications from known providers (AWS, Google, Microsoft, Coursera, etc.) and covers_skills must list which missing skills they address.
- quick_wins should be things achievable in 1-2 weeks that would noticeably improve the match score.
- resume_update_tips should suggest how to better highlight existing skills that match the JD.
"""


ATS_AUDIT_PROMPT = """
You are an ATS (Applicant Tracking System) compliance expert. Analyze this resume for ATS compatibility and provide a detailed audit.

RESUME TEXT:
{resume_text}

TARGET JOB KEYWORDS:
{jd_keywords}

Perform a comprehensive ATS audit and return ONLY valid JSON:
{{
  "ats_grade": "A+|A|B+|B|C+|C|D|F",
  "pass_probability": 0,
  "section_analysis": {{
    "found": [],
    "missing": [],
    "order_assessment": "",
    "recommendations": []
  }},
  "keyword_analysis": {{
    "well_placed": [],
    "missing_critical": [],
    "overused": [],
    "density_assessment": ""
  }},
  "formatting_analysis": {{
    "issues": [],
    "parsability_score": 0,
    "recommendations": []
  }},
  "content_quality": {{
    "action_verb_assessment": "",
    "quantification_level": "",
    "bullet_structure": "",
    "recommendations": []
  }},
  "top_5_improvements": [
    {{
      "priority": 1,
      "area": "",
      "action": "",
      "expected_impact": ""
    }}
  ],
  "overall_assessment": ""
}}

RULES:
- pass_probability is 0-100 estimating likelihood of passing ATS screening.
- Be brutally honest but constructive.
- top_5_improvements should be the highest-impact changes, ranked by priority.
- Consider real ATS systems like Taleo, Workday, Greenhouse, Lever, iCIMS.
"""


ROADMAP_BUILDER_PROMPT = """
You are an expert career and technology roadmap architect. Create a comprehensive, hierarchical learning roadmap for the given topic — structured exactly like roadmap.sh with branching topic trees.

USER INPUT:
{user_input}

CONTEXT: {context}

Generate a detailed roadmap organized into logical sections. Each section has sub-topics that branch out, and each sub-topic has individual skills/tools as leaf nodes.

Return ONLY valid JSON:
{{
  "title": "Roadmap title (e.g. 'Machine Learning Engineer Roadmap')",
  "description": "2-3 sentence overview of this learning path",
  "estimated_total_months": 0,
  "sections": [
    {{
      "name": "Section name (e.g. 'Programming Fundamentals')",
      "order": 1,
      "description": "What this section covers",
      "sub_topics": [
        {{
          "name": "Sub-topic name (e.g. 'Languages', 'Tools', 'Core Concepts')",
          "skills": [
            {{
              "name": "Skill or tool name",
              "priority": "must_learn|should_learn|nice_to_know",
              "description": "1-2 sentence description",
              "resources": [
                {{
                  "title": "",
                  "url": "",
                  "type": "course|docs|tutorial|book|video|project"
                }}
              ],
              "estimated_hours": 0
            }}
          ]
        }}
      ]
    }}
  ],
  "certifications": [
    {{
      "name": "",
      "provider": "",
      "url": "",
      "covers_section": "",
      "priority": "high|medium|low"
    }}
  ],
  "career_progression": ["Junior role", "Mid role", "Senior role"],
  "related_roadmaps": ["other topics the learner should explore"]
}}

RULES:
- Create 6-12 sections, ordered from foundational to advanced. Each section should have 1-4 sub_topics.
- Each sub_topic groups 2-5 related skills/tools (e.g. "Languages" → Python, SQL, Go).
- Mark skills as must_learn (essential), should_learn (recommended), or nice_to_know (optional).
- Include REAL resources with actual URLs (official docs, freeCodeCamp, Coursera, YouTube, MDN, etc.).
- Be comprehensive and detailed like roadmap.sh — cover the full journey from beginner to production-ready.
- Each section should build on the previous one logically.
- Certifications must be REAL, verifiable certifications from known providers.
- estimated_total_months should be a realistic estimate for someone learning part-time.
- Think of the visual as a tree: section headers are the spine, sub-topics branch left/right, skills are leaf nodes.
"""

