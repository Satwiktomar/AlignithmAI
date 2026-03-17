from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import JobDescription
from app.schemas import JobDescriptionCreate, JobDescriptionOut
from app.api.routes.auth import get_current_user
from app.models import User
from app.services.scraper import scrape_job_url
from app.services.gemini import generate_json, embed_text, get_ai_config
from app.prompts import JD_PARSE_PROMPT
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])

MAX_RAW_TEXT_LENGTH = 20_000


@router.post("/parse", response_model=JobDescriptionOut)
async def parse_job(
    job_data: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw_text = job_data.raw_text or ""

    if raw_text and len(raw_text) > MAX_RAW_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Job description text too long ({len(raw_text)} chars). Maximum is {MAX_RAW_TEXT_LENGTH} characters."
        )

    if job_data.source_url:
        parsed_url = job_data.source_url.strip()
        if not parsed_url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")
        if not raw_text:
            try:
                raw_text = await scrape_job_url(parsed_url)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Could not scrape URL: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="No job description text provided")

    prompt = JD_PARSE_PROMPT.format(jd_text=raw_text[:6000])
    api_key, provider = get_ai_config(current_user)
    parsed = await generate_json(prompt, user_api_key=api_key, use_local_model=current_user.prefer_local_model, provider=provider)

    # Generate embedding once and store for reuse
    job_embedding = None
    try:
        if api_key:
            job_embedding = embed_text(raw_text, user_api_key=api_key, provider=provider)
    except Exception as e:
        logger.warning(f"Failed to generate job embedding: {e}")

    job = JobDescription(
        user_id=current_user.id,
        raw_text=raw_text,
        parsed_json=parsed,
        embedding=job_embedding,
        source_url=job_data.source_url,
        company_name=job_data.company_name or parsed.get("company", ""),
        job_title=job_data.job_title or parsed.get("job_title", "")
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/", response_model=list[JobDescriptionOut])
def list_jobs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(JobDescription).filter(JobDescription.user_id == current_user.id).order_by(JobDescription.created_at.desc()).all()


@router.get("/{job_id}", response_model=JobDescriptionOut)
def get_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job description deleted"}
