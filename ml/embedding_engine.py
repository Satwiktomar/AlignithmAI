"""
Embedding Engine — Gemini text-embedding-004 with in-memory caching.

Uses Google Gemini embedding API for semantic similarity with an
in-memory hash-based cache to avoid redundant API calls.
"""

import os
import hashlib
import time
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-004"


# ── Gemini Client ───────────────────────────────────────────────────────

_client = None


def _get_client():
    """Lazy-init the genai client."""
    global _client
    if _client is not None:
        return _client
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set")
    _client = genai.Client(api_key=api_key)
    logger.info(f"Gemini embedding client initialized (model={EMBEDDING_MODEL})")
    return _client


# ── Embedding Cache ─────────────────────────────────────────────────────

class EmbeddingCache:
    """In-memory embedding cache with TTL (default 1 hour)."""

    def __init__(self, ttl_seconds: int = 3600, max_entries: int = 500):
        self._cache: dict[str, tuple[np.ndarray, float]] = {}
        self._ttl = ttl_seconds
        self._max_entries = max_entries
        self._hits = 0
        self._misses = 0

    def _key(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> np.ndarray | None:
        key = self._key(text)
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        vec, ts = entry
        if time.time() - ts > self._ttl:
            del self._cache[key]
            self._misses += 1
            return None
        self._hits += 1
        return vec

    def put(self, text: str, vec: np.ndarray) -> None:
        if len(self._cache) >= self._max_entries:
            sorted_keys = sorted(self._cache, key=lambda k: self._cache[k][1])
            for k in sorted_keys[:len(sorted_keys) // 10]:
                del self._cache[k]
        self._cache[self._key(text)] = (vec, time.time())

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "cache_size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / max(total, 1) * 100, 1),
        }

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0


_cache = EmbeddingCache(max_entries=500)


# ── Core Embedding Function ────────────────────────────────────────────

def _embed_single(text: str) -> np.ndarray:
    """Call Gemini embed_content for a single text."""
    client = _get_client()
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    return np.array(response.embeddings[0].values, dtype=np.float32)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Encode texts with cache-first lookup. Only calls API for cache misses."""
    results = [None] * len(texts)
    to_encode_indices = []
    to_encode_texts = []

    for i, text in enumerate(texts):
        cached = _cache.get(text)
        if cached is not None:
            results[i] = cached
        else:
            to_encode_indices.append(i)
            to_encode_texts.append(text)

    if to_encode_texts:
        for idx, text in zip(to_encode_indices, to_encode_texts):
            vec = _embed_single(text)
            _cache.put(text, vec)
            results[idx] = vec

    return np.array(results)


# ── Similarity Functions ────────────────────────────────────────────────

def cosine_sim(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    return float(cosine_similarity(vec_a.reshape(1, -1), vec_b.reshape(1, -1))[0][0])


def semantic_similarity(text_a: str, text_b: str) -> float:
    vecs = embed_texts([text_a, text_b])
    return cosine_sim(vecs[0], vecs[1])


def batch_similarity(query: str, candidates: list[str]) -> list[float]:
    if not candidates:
        return []
    all_texts = [query] + candidates
    vecs = embed_texts(all_texts)
    query_vec = vecs[0:1]
    candidate_vecs = vecs[1:]
    sims = cosine_similarity(query_vec, candidate_vecs)[0]
    return [float(sc) for sc in sims]


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


# ── Cache Management ────────────────────────────────────────────────────

def get_cache_stats() -> dict:
    return _cache.stats()


def clear_cache() -> dict:
    _cache.clear()
    return {"message": "Cache cleared"}
