from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, JobDescription
from app.schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.api.routes.auth import get_current_user
from app.models import User
from app.services.gemini import generate_json, get_ai_config
from app.prompts import PROJECT_RANK_PROMPT
import json

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectOut)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_project = Project(user_id=current_user.id, **project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, project_data: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}


@router.post("/recommend")
async def recommend_projects(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")

    projects_data = [{"id": p.id, "title": p.title, "description": p.description, "skills": p.skills_json, "domain": p.domain, "tags": p.tags, "metrics": p.metrics_json} for p in projects]
    prompt = PROJECT_RANK_PROMPT.format(
        projects_json=json.dumps(projects_data, indent=2),
        jd_json=json.dumps(job.parsed_json, indent=2)[:3000]
    )
    api_key, provider = get_ai_config(current_user)
    result = await generate_json(prompt, user_api_key=api_key, provider=provider)
    return result
