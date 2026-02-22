from fastapi import APIRouter
from pydantic import BaseModel
from ats_scorer import compute_ats_score, detect_ats_issues, detect_redundancy, compute_keyword_coverage

router = APIRouter(prefix="/ats", tags=["ats"])


class ATSRequest(BaseModel):
    resume_text: str
    jd_keywords: list[str] = []
    required_skills: list[str] = []
    preferred_skills: list[str] = []


class RedundancyRequest(BaseModel):
    text: str


@router.post("/score")
def ats_score(req: ATSRequest):
    result = compute_ats_score(req.resume_text, req.jd_keywords, req.required_skills, req.preferred_skills)
    issues = detect_ats_issues(req.resume_text)
    result["ats_issues"] = issues
    return result


@router.post("/redundancy")
def check_redundancy(req: RedundancyRequest):
    issues = detect_redundancy(req.text)
    return {"issues": issues, "count": len(issues)}


@router.post("/keyword-coverage")
def keyword_coverage(req: ATSRequest):
    return compute_keyword_coverage(req.resume_text, req.jd_keywords)
