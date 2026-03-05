"""
Embedding Engine — Sentence-Transformer embeddings with caching.

Uses all-MiniLM-L6-v2 for semantic similarity with an in-memory
hash-based cache to avoid re-encoding identical texts.
"""

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import hashlib
import time
import logging
import threading

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"

# ── Embedding Cache ─────────────────────────────────────────────────────

class EmbeddingCache:
    """In-memory embedding cache with TTL (default 1 hour)."""

    def __init__(self, ttl_seconds: int = 3600, max_entries: int = 5000):
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
            # Evict oldest 10%
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


# Global cache instance (lower max_entries to save memory on constrained hosts)
_cache = EmbeddingCache(max_entries=500)


# ── Model Loading ───────────────────────────────────────────────────────

_model = None
_model_lock = threading.Lock()


def get_model():
    """Lazy-load the SentenceTransformer model on first use (thread-safe).

    The import is deferred so that the sentence_transformers library
    (and PyTorch/ONNX) are NOT loaded at application startup time.
    This keeps the cold-start memory footprint under ~80 MB, which is
    critical for Render free tier (512 MB limit).
    """
    global _model
    if _model is not None:
        return _model
    with _model_lock:
        if _model is not None:
            return _model  # another thread loaded while we waited
        from sentence_transformers import SentenceTransformer  # lazy import
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
        logger.info(f"Model loaded: {MODEL_NAME} (dim={_model.get_sentence_embedding_dimension()})")
        return _model


def warmup_model() -> dict:
    """Pre-warm the model by encoding a test sentence. Call at startup."""
    model = get_model()
    _ = model.encode(["warmup"], normalize_embeddings=True)
    return {
        "model": MODEL_NAME,
        "dimension": model.get_sentence_embedding_dimension(),
        "status": "ready",
    }


# ── Core Functions ──────────────────────────────────────────────────────

def embed_texts(texts: list[str]) -> np.ndarray:
    """Encode texts with cache-first lookup. Only encodes cache misses."""
    model = get_model()
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
        new_vecs = model.encode(to_encode_texts, normalize_embeddings=True)
        for idx, text, vec in zip(to_encode_indices, to_encode_texts, new_vecs):
            _cache.put(text, vec)
            results[idx] = vec

    return np.array(results)


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

    # Vectorized cosine similarity
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
