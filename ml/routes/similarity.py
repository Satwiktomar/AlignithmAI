from fastapi import APIRouter
from pydantic import BaseModel
from embedding_engine import semantic_similarity, batch_similarity, rank_projects_by_jd

router = APIRouter(prefix="/similarity", tags=["similarity"])


class SimilarityRequest(BaseModel):
    text_a: str
    text_b: str


class BatchSimilarityRequest(BaseModel):
    query: str
    candidates: list[str]


class ProjectRankRequest(BaseModel):
    jd_text: str
    projects: list[dict]


@router.post("/semantic")
def compute_semantic_similarity(req: SimilarityRequest):
    score = semantic_similarity(req.text_a, req.text_b)
    return {"similarity": round(score * 100, 2), "raw": score}


@router.post("/batch")
def compute_batch_similarity(req: BatchSimilarityRequest):
    scores = batch_similarity(req.query, req.candidates)
    ranked = sorted(
        [{"candidate": c, "score": round(s * 100, 2)} for c, s in zip(req.candidates, scores)],
        key=lambda x: x["score"],
        reverse=True
    )
    return {"results": ranked}


@router.post("/rank-projects")
def rank_projects(req: ProjectRankRequest):
    ranked = rank_projects_by_jd(req.jd_text, req.projects)
    return {"ranked_projects": ranked}
