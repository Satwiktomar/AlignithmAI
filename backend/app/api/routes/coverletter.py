from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.limiter import limiter
from app.models import CoverLetter, Resume, JobDescription
from app.schemas import CoverLetterCreate, CoverLetterOut
from app.api.routes.auth import get_current_user
from app.models import User
from app.services.gemini import generate, get_ai_config
from app.prompts import COVER_LETTER_PROMPT
import json

router = APIRouter(prefix="/coverletter", tags=["coverletter"])

VALID_TONES = ["formal", "semi-formal", "startup", "direct", "corporate"]


@router.post("/generate", response_model=CoverLetterOut)
@limiter.limit("30/minute")
async def generate_cover_letter(
    request: Request,
    cl_data: CoverLetterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == cl_data.resume_id, Resume.user_id == current_user.id).first()
    job = db.query(JobDescription).filter(JobDescription.id == cl_data.job_id, JobDescription.user_id == current_user.id).first()

    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or job not found")

    tone = cl_data.tone if cl_data.tone in VALID_TONES else "semi-formal"
    prompt = COVER_LETTER_PROMPT.format(
        tone=tone,
        resume_json=json.dumps(resume.parsed_json, indent=2)[:4000],
        jd_json=json.dumps(job.parsed_json, indent=2)[:3000]
    )
    api_key, provider = get_ai_config(current_user)
    generated_text = await generate(prompt, user_api_key=api_key, use_local_model=current_user.prefer_local_model, provider=provider)

    cl = CoverLetter(
        user_id=current_user.id,
        job_id=cl_data.job_id,
        generated_text=generated_text,
        tone=tone
    )
    db.add(cl)
    db.commit()
    db.refresh(cl)
    return cl


@router.get("/", response_model=list[CoverLetterOut])
def list_cover_letters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(CoverLetter).filter(CoverLetter.user_id == current_user.id).order_by(CoverLetter.created_at.desc()).all()


@router.get("/{cl_id}", response_model=CoverLetterOut)
def get_cover_letter(cl_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cl = db.query(CoverLetter).filter(CoverLetter.id == cl_id, CoverLetter.user_id == current_user.id).first()
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return cl


@router.delete("/{cl_id}")
def delete_cover_letter(cl_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cl = db.query(CoverLetter).filter(CoverLetter.id == cl_id, CoverLetter.user_id == current_user.id).first()
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    db.delete(cl)
    db.commit()
    return {"message": "Cover letter deleted"}
