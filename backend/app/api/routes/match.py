from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Resume, JobDescription, MatchScore
from app.schemas import MatchScoreOut
from app.api.routes.auth import get_current_user
from app.models import User
from app.services.gemini import generate_json, get_ai_config
from app.prompts import MATCH_ENGINE_PROMPT, RESUME_SUGGEST_PROMPT
import json

router = APIRouter(prefix="/match", tags=["match"])


@router.post("/", response_model=MatchScoreOut)
async def run_match(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    prompt = MATCH_ENGINE_PROMPT.format(
        resume_json=json.dumps(resume.parsed_json, indent=2)[:4000],
        jd_json=json.dumps(job.parsed_json, indent=2)[:4000]
    )
    api_key, provider = get_ai_config(current_user)
    result = await generate_json(prompt, user_api_key=api_key, use_local_model=current_user.prefer_local_model, provider=provider)

    ms = MatchScore(
        user_id=current_user.id,
        resume_id=resume_id,
        job_id=job_id,
        overall_score=float(result.get("overall_score", 0)),
        keyword_score=float(result.get("keyword_score", 0)),
        skill_score=float(result.get("skill_score", 0)),
        experience_score=float(result.get("experience_score", 0)),
        ats_score=float(result.get("ats_score", 0)),
        details_json=result
    )
    db.add(ms)
    db.commit()
    db.refresh(ms)
    return ms


@router.get("/", response_model=list[MatchScoreOut])
def list_matches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(MatchScore).filter(MatchScore.user_id == current_user.id).order_by(MatchScore.created_at.desc()).all()


@router.get("/{match_id}", response_model=MatchScoreOut)
def get_match(match_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ms = db.query(MatchScore).filter(MatchScore.id == match_id, MatchScore.user_id == current_user.id).first()
    if not ms:
        raise HTTPException(status_code=404, detail="Match score not found")
    return ms


@router.post("/suggest")
async def get_suggestions(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or job not found")

    jd_keywords = job.parsed_json.get("keywords", []) + job.parsed_json.get("required_skills", []) if job.parsed_json else []
    prompt = RESUME_SUGGEST_PROMPT.format(
        resume_json=json.dumps(resume.parsed_json, indent=2)[:4000],
        jd_keywords=json.dumps(jd_keywords)
    )
    api_key, provider = get_ai_config(current_user)
    result = await generate_json(prompt, user_api_key=api_key, use_local_model=current_user.prefer_local_model, provider=provider)
    return result


@router.post("/enhanced")
async def run_enhanced_match(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enhanced match combining ML-computed ATS scores with Gemini AI analysis."""
    import httpx
    import os

    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    ml_url = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    jd_data = job.parsed_json or {}

    ml_ats_result = {}
    ml_internal_key = os.getenv("ML_INTERNAL_KEY", "")
    ml_headers = {"X-Internal-Key": ml_internal_key} if ml_internal_key else {}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            ml_response = await client.post(f"{ml_url}/ats/full-audit", json={
                "resume_text": resume.raw_text or "",
                "jd_keywords": jd_data.get("ats_keywords", []) + jd_data.get("keywords", []),
                "required_skills": jd_data.get("required_skills", []),
                "preferred_skills": jd_data.get("preferred_skills", []),
            }, headers=ml_headers)
            if ml_response.status_code == 200:
                ml_ats_result = ml_response.json()
    except Exception:
        pass  # ML service unavailable — proceed with Gemini only

    # 2. Get Gemini AI analysis
    prompt = MATCH_ENGINE_PROMPT.format(
        resume_json=json.dumps(resume.parsed_json, indent=2)[:4000],
        jd_json=json.dumps(job.parsed_json, indent=2)[:4000]
    )
    api_key, provider = get_ai_config(current_user)
    ai_result = await generate_json(prompt, user_api_key=api_key, use_local_model=current_user.prefer_local_model, provider=provider)

    # 3. Merge: use ML scores where available, AI for qualitative
    combined = {
        **ai_result,
        "ml_ats_audit": ml_ats_result,
        "enhanced": True,
    }

    # Persist match score
    ms = MatchScore(
        user_id=current_user.id,
        resume_id=resume_id,
        job_id=job_id,
        overall_score=float(ai_result.get("overall_score", 0)),
        keyword_score=float(ai_result.get("keyword_score", 0)),
        skill_score=float(ai_result.get("skill_score", 0)),
        experience_score=float(ai_result.get("experience_score", 0)),
        ats_score=float(ml_ats_result.get("overall_ats_score", ai_result.get("ats_score", 0))),
        details_json=combined
    )
    db.add(ms)
    db.commit()
    db.refresh(ms)

    return combined


@router.post("/ats-audit")
async def ats_audit(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dedicated ATS compliance audit combining ML scoring with AI analysis."""
    import httpx
    import os
    from app.prompts import ATS_AUDIT_PROMPT

    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or job not found")

    ml_url = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    jd_data = job.parsed_json or {}
    all_keywords = jd_data.get("ats_keywords", []) + jd_data.get("keywords", []) + jd_data.get("required_skills", [])

    ml_result = {}
    ml_internal_key = os.getenv("ML_INTERNAL_KEY", "")
    ml_headers = {"X-Internal-Key": ml_internal_key} if ml_internal_key else {}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{ml_url}/ats/full-audit", json={
                "resume_text": resume.raw_text or "",
                "jd_keywords": all_keywords,
                "required_skills": jd_data.get("required_skills", []),
                "preferred_skills": jd_data.get("preferred_skills", []),
            }, headers=ml_headers)
            if resp.status_code == 200:
                ml_result = resp.json()
    except Exception:
        pass

    # AI audit
    prompt = ATS_AUDIT_PROMPT.format(
        resume_text=(resume.raw_text or "")[:8000],
        jd_keywords=json.dumps(all_keywords[:30])
    )
    api_key, provider = get_ai_config(current_user)
    ai_result = await generate_json(prompt, user_api_key=api_key, use_local_model=current_user.prefer_local_model, provider=provider)

    return {
        "ml_audit": ml_result,
        "ai_audit": ai_result,
    }
