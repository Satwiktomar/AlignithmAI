from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.limiter import limiter
from app.models import Resume, JobDescription, MatchScore, Project, CoverLetter
from app.api.routes.auth import get_current_user
from app.models import User
from app.services.auth import decrypt_api_key
from app.services.gemini import generate_json, generate_text
from app.services.ollama_service import get_ollama_status
from app.prompts import SKILL_GAP_PROMPT, RECRUITER_SIM_PROMPT, ROADMAP_BUILDER_PROMPT
import json
import re
from collections import Counter
from datetime import date

router = APIRouter(prefix="/advanced", tags=["advanced"])


@router.post("/skillgap")
@limiter.limit("30/minute")
async def get_skill_gap(
    request: Request,
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or job not found")

    match = db.query(MatchScore).filter(
        MatchScore.resume_id == resume_id,
        MatchScore.job_id == job_id,
        MatchScore.user_id == current_user.id
    ).order_by(MatchScore.created_at.desc()).first()

    match_json = json.dumps(match.details_json, indent=2)[:2000] if match else "{}"
    resume_skills = json.dumps(resume.parsed_json.get("skills", {}) if resume.parsed_json else {}, indent=2)
    jd_skills = json.dumps({
        "required": job.parsed_json.get("required_skills", []) if job.parsed_json else [],
        "preferred": job.parsed_json.get("preferred_skills", []) if job.parsed_json else []
    }, indent=2)

    prompt = SKILL_GAP_PROMPT.format(
        current_date=date.today().strftime("%B %d, %Y"),
        match_json=match_json,
        resume_skills=resume_skills,
        jd_skills=jd_skills
    )
    result = await generate_json(prompt, user_api_key=decrypt_api_key(current_user.gemini_api_key), use_local_model=current_user.prefer_local_model)
    return result


@router.post("/recruiter-sim")
@limiter.limit("30/minute")
async def recruiter_simulation(
    request: Request,
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or job not found")

    prompt = RECRUITER_SIM_PROMPT.format(
        current_date=date.today().strftime("%B %d, %Y"),
        resume_json=json.dumps(resume.parsed_json, indent=2)[:6000],
        jd_json=json.dumps(job.parsed_json, indent=2)[:4000]
    )
    result = await generate_json(prompt, user_api_key=decrypt_api_key(current_user.gemini_api_key), use_local_model=current_user.prefer_local_model)
    return result


@router.get("/dashboard-stats")
def dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resumes_count = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    projects_count = db.query(Project).filter(Project.user_id == current_user.id).count()
    jobs_count = db.query(JobDescription).filter(JobDescription.user_id == current_user.id).count()
    cl_count = db.query(CoverLetter).filter(CoverLetter.user_id == current_user.id).count()
    match_scores = db.query(MatchScore).filter(MatchScore.user_id == current_user.id).order_by(MatchScore.created_at.desc()).limit(5).all()

    return {
        "resumes": resumes_count,
        "projects": projects_count,
        "jobs": jobs_count,
        "cover_letters": cl_count,
        "recent_matches": [
            {
                "id": ms.id,
                "overall_score": ms.overall_score,
                "job_id": ms.job_id,
                "resume_id": ms.resume_id,
                "created_at": ms.created_at.isoformat()
            }
            for ms in match_scores
        ]
    }


AI_TONE_PHRASES = [
    "i am excited to", "i am passionate about", "i would be a great fit",
    "looking forward to", "thank you for your consideration", "dynamic team",
    "synergy", "leverage my skills", "results-driven", "go-getter",
    "team player", "hard worker", "self-motivated", "detail-oriented",
    "thinking outside the box", "fast-paced environment", "cutting-edge",
    "proven track record", "strong communication skills", "highly motivated",
    "seeking to leverage", "best of breed", "move the needle", "deep dive",
    "circle back", "bandwidth", "game changer", "delighted to apply",
    "thrilled to apply", "enthusiastic about"
]

VAGUE_PHRASES = [
    "responsible for", "duties included", "worked on", "helped with",
    "assisted in", "various tasks", "and more", "participated in",
    "involved in", "part of a team that"
]


class TextAnalysisRequest(BaseModel):
    text: str


@router.post("/tone-detect")
def detect_ai_tone(req: TextAnalysisRequest, current_user: User = Depends(get_current_user)):
    text_lower = req.text.lower()
    flagged_ai = [p for p in AI_TONE_PHRASES if p in text_lower]
    flagged_vague = [p for p in VAGUE_PHRASES if p in text_lower]
    exclamation_count = req.text.count("!")
    passive_matches = re.findall(r'\b(was|were|been|being|is|are)\s+\w+ed\b', req.text, re.I)

    total_flags = len(flagged_ai) + len(flagged_vague)
    penalty = min(total_flags * 8 + exclamation_count * 3 + len(passive_matches) * 2, 100)
    tone_score = max(0, 100 - penalty)

    verdict = (
        "✅ Sounds human and authentic" if tone_score >= 80
        else "⚠️ Some AI patterns detected — review flagged phrases" if tone_score >= 50
        else "❌ Heavy AI/robotic tone — significant rewrite recommended"
    )

    return {
        "tone_score": tone_score,
        "verdict": verdict,
        "flagged_ai_phrases": flagged_ai,
        "flagged_vague_phrases": flagged_vague,
        "exclamation_marks": exclamation_count,
        "passive_voice_instances": len(passive_matches),
        "improvement_tips": (
            [f"Replace '{p}' with a specific evidence-backed statement" for p in flagged_ai[:3]] +
            [f"Strengthen '{p}' with an action verb + metric" for p in flagged_vague[:3]]
        )
    }


@router.post("/bias-detect")
def detect_bias_redundancy(req: TextAnalysisRequest, current_user: User = Depends(get_current_user)):
    text = req.text
    sentences = [s.strip() for s in re.split(r'[.\n]', text) if len(s.strip()) > 15]
    seen = Counter()
    for s in sentences:
        key = " ".join(s.lower().split()[:5])
        seen[key] += 1
    repeated = {k: v for k, v in seen.items() if v > 1}

    filler = ["basically", "literally", "very", "really", "quite", "just",
              "actually", "in terms of", "at the end of the day", "needless to say"]
    bias_terms = ["native speaker", "mother tongue", "young professional"]
    found_filler = [f for f in filler if f in text.lower()]
    found_bias = [b for b in bias_terms if b in text.lower()]

    return {
        "repeated_sentence_starts": repeated,
        "filler_language_found": found_filler,
        "potential_bias_terms": found_bias,
        "total_issues": len(repeated) + len(found_filler) + len(found_bias),
        "advice": (
            "Clean — no significant bias or redundancy detected" if not repeated and not found_filler
            else "Review highlighted items before submitting"
        )
    }


INDUSTRY_MODE_PROMPTS = {
    "bigtech": "Calibrate this resume for a Big Tech company (Google/Meta/Amazon). Emphasize scale, system complexity, measurable impact (metrics), cross-functional collaboration, technical depth. Action verbs: architected, optimized, reduced, scaled, shipped.",
    "startup": "Calibrate this resume for a startup. Emphasize ownership, speed, wearing multiple hats, direct product impact, initiative. Use direct energetic language.",
    "consulting": "Calibrate this resume for consulting (McKinsey/BCG/Deloitte). Emphasize problem-solving, client-facing impact, business outcomes, quantified ROI, structured thinking.",
    "research": "Calibrate this resume for academic/research roles. Emphasize publications, novel contributions, methodology rigor, domain expertise, collaboration with researchers.",
}


class IndustryModeRequest(BaseModel):
    resume_id: int
    industry_mode: str


@router.post("/industry-mode")
@limiter.limit("30/minute")
async def industry_mode_calibration(
    request: Request,
    req: IndustryModeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == req.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    mode_instruction = INDUSTRY_MODE_PROMPTS.get(req.industry_mode)
    if not mode_instruction:
        raise HTTPException(status_code=400, detail="Unknown industry mode. Use: bigtech|startup|consulting|research")

    prompt = f"""
{mode_instruction}

CURRENT RESUME (use ONLY this — do NOT invent experience):
{json.dumps(resume.parsed_json, indent=2)[:5000]}

Return ONLY valid JSON:
{{
  "industry_mode": "{req.industry_mode}",
  "calibrated_summary": "",
  "calibrated_bullets": [
    {{
      "original": "",
      "rewritten": "",
      "reason": ""
    }}
  ],
  "tone_keywords_added": [],
  "tone_keywords_removed": [],
  "overall_advice": ""
}}
"""
    result = await generate_json(prompt, user_api_key=decrypt_api_key(current_user.gemini_api_key), use_local_model=current_user.prefer_local_model)
    return result


@router.get("/ollama-status")
async def ollama_status(current_user: User = Depends(get_current_user)):
    return await get_ollama_status()


class RoadmapRequest(BaseModel):
    topic: str
    context: str = "general"
    force_new: bool = False


@router.post("/roadmap-builder")
@limiter.limit("20/minute")
async def build_roadmap(
    request: Request,
    req: RoadmapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not req.topic or len(req.topic.strip()) < 2:
        raise HTTPException(status_code=400, detail="Please provide a topic or job description.")

    topic_key = re.sub(r'\s+', ' ', req.topic.strip().lower())[:500]

    # Check cache first (unless force_new)
    if not req.force_new:
        from app.models import CachedRoadmap
        cached = db.query(CachedRoadmap).filter(
            CachedRoadmap.user_id == current_user.id,
            CachedRoadmap.topic_key == topic_key
        ).order_by(CachedRoadmap.created_at.desc()).first()
        if cached:
            return {"cached": True, "id": cached.id, **cached.result_json}

    prompt = ROADMAP_BUILDER_PROMPT.format(
        user_input=req.topic[:3000],
        context=req.context[:500]
    )
    result = await generate_json(
        prompt,
        user_api_key=decrypt_api_key(current_user.gemini_api_key),
        use_local_model=current_user.prefer_local_model
    )

    # Save to cache (only if generation succeeded)
    if isinstance(result, dict) and not result.get("error"):
        from app.models import CachedRoadmap
        cached_entry = CachedRoadmap(
            user_id=current_user.id,
            topic_key=topic_key,
            topic_display=req.topic.strip()[:500],
            result_json=result,
        )
        db.add(cached_entry)
        db.commit()
        db.refresh(cached_entry)
        result["cached"] = False
        result["id"] = cached_entry.id

    return result


@router.get("/cached-roadmaps")
def list_cached_roadmaps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models import CachedRoadmap
    cached = db.query(CachedRoadmap).filter(
        CachedRoadmap.user_id == current_user.id
    ).order_by(CachedRoadmap.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "topic": c.topic_display,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in cached
    ]


@router.delete("/cached-roadmaps/{roadmap_id}")
def delete_cached_roadmap(
    roadmap_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models import CachedRoadmap
    cached = db.query(CachedRoadmap).filter(
        CachedRoadmap.id == roadmap_id,
        CachedRoadmap.user_id == current_user.id
    ).first()
    if not cached:
        raise HTTPException(status_code=404, detail="Cached roadmap not found")
    db.delete(cached)
    db.commit()
    return {"detail": "Cached roadmap deleted"}

