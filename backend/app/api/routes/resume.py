from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Resume, ResumeVersion, JobDescription, MatchScore
from app.schemas import ResumeOut, ResumeVersionOut, ResumeVersionCreate
from app.api.routes.auth import get_current_user
from app.models import User
from app.services.parser import extract_text
from app.services.auth import decrypt_api_key
from app.services.gemini import generate_json
from app.prompts import RESUME_PARSE_PROMPT
import json
from datetime import date

router = APIRouter(prefix="/resume", tags=["resume"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(file_bytes) // (1024*1024)}MB). Maximum is 10MB."
        )

    if not file_bytes:
        raise HTTPException(status_code=400, detail="File is empty")

    raw_text = extract_text(file.filename, file_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    prompt = RESUME_PARSE_PROMPT.format(
        current_date=date.today().strftime("%B %d, %Y"),
        resume_text=raw_text[:12000]
    )
    parsed = await generate_json(prompt, user_api_key=decrypt_api_key(current_user.gemini_api_key), use_local_model=current_user.prefer_local_model)

    resume = Resume(
        user_id=current_user.id,
        original_filename=file.filename,
        raw_text=raw_text,
        parsed_json=parsed
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted"}


@router.post("/{resume_id}/versions", response_model=ResumeVersionOut)
def save_version(
    resume_id: int,
    version_data: ResumeVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    match_score = None
    if version_data.job_id:
        ms = db.query(MatchScore).filter(
            MatchScore.resume_id == resume_id,
            MatchScore.job_id == version_data.job_id,
            MatchScore.user_id == current_user.id
        ).order_by(MatchScore.created_at.desc()).first()
        if ms:
            match_score = ms.overall_score

    version = ResumeVersion(
        resume_id=resume_id,
        job_id=version_data.job_id,
        version_label=version_data.version_label,
        content_json=resume.parsed_json,
        match_score=match_score
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.get("/{resume_id}/versions", response_model=list[ResumeVersionOut])
def list_versions(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume_id).order_by(ResumeVersion.created_at.desc()).all()


class VersionSavePayload(BaseModel):
    resume_id: int
    job_id: int | None = None
    version_label: str = "Untitled Version"
    notes: str | None = None


@router.post("/version", response_model=ResumeVersionOut)
def save_version_flat(
    payload: VersionSavePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    match_score = None
    if payload.job_id:
        ms = db.query(MatchScore).filter(
            MatchScore.resume_id == payload.resume_id,
            MatchScore.job_id == payload.job_id,
            MatchScore.user_id == current_user.id
        ).order_by(MatchScore.created_at.desc()).first()
        if ms:
            match_score = ms.overall_score

    version = ResumeVersion(
        resume_id=payload.resume_id,
        job_id=payload.job_id,
        version_label=payload.version_label,
        content_json=resume.parsed_json,
        match_score=match_score,
        notes=payload.notes
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.delete("/version/{version_id}")
def delete_version(version_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    v = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    resume = db.query(Resume).filter(Resume.id == v.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(v)
    db.commit()
    return {"message": "Version deleted"}
