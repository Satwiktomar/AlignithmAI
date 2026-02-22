from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import JobDescription
from app.schemas import JobDescriptionCreate, JobDescriptionOut
from app.api.routes.auth import get_current_user
from app.models import User
from app.services.scraper import scrape_job_url
from app.services.gemini import generate_json
from app.prompts import JD_PARSE_PROMPT

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/parse", response_model=JobDescriptionOut)
async def parse_job(
    job_data: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw_text = job_data.raw_text or ""

    if job_data.source_url and not raw_text:
        try:
            raw_text = await scrape_job_url(job_data.source_url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not scrape URL: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="No job description text provided")

    prompt = JD_PARSE_PROMPT.format(jd_text=raw_text[:6000])
    parsed = await generate_json(prompt)

    job = JobDescription(
        user_id=current_user.id,
        raw_text=raw_text,
        parsed_json=parsed,
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
