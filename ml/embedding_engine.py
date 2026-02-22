from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from functools import lru_cache

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_model()
    return model.encode(texts, normalize_embeddings=True)


def cosine_sim(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    return float(cosine_similarity(vec_a.reshape(1, -1), vec_b.reshape(1, -1))[0][0])


def semantic_similarity(text_a: str, text_b: str) -> float:
    vecs = embed_texts([text_a, text_b])
    return cosine_sim(vecs[0], vecs[1])


def batch_similarity(query: str, candidates: list[str]) -> list[float]:
    all_texts = [query] + candidates
    vecs = embed_texts(all_texts)
    query_vec = vecs[0]
    return [cosine_sim(query_vec, vecs[i + 1]) for i in range(len(candidates))]


def rank_projects_by_jd(jd_text: str, projects: list[dict]) -> list[dict]:
    if not projects:
        return []

    project_texts = []
    for p in projects:
        skills_str = " ".join(p.get("skills", []) or [])
        text = f"{p.get('title', '')} {p.get('description', '')} {skills_str}"
        project_texts.append(text)

    scores = batch_similarity(jd_text, project_texts)

    ranked = []
    for p, score in zip(projects, scores):
        ranked.append({**p, "relevance_score": round(score * 100, 2)})

    ranked.sort(key=lambda x: x["relevance_score"], reverse=True)
    return ranked
