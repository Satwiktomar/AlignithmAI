from fastapi import APIRouter
from pydantic import BaseModel
from skill_taxonomy import normalize_skill, normalize_skills, find_skill_overlap

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


class NormalizeRequest(BaseModel):
    skills: list[str]


class OverlapRequest(BaseModel):
    resume_skills: list[str]
    jd_skills: list[str]


@router.post("/normalize")
def normalize(req: NormalizeRequest):
    return {"normalized": normalize_skills(req.skills)}


@router.post("/overlap")
def skill_overlap(req: OverlapRequest):
    return find_skill_overlap(req.resume_skills, req.jd_skills)
