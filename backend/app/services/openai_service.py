"""OpenAI LLM service — text generation and embeddings via the OpenAI API."""

import os
import json
import asyncio
import logging
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
_MAX_RETRIES = 3
_BASE_DELAY = 2


def _get_openai_client(api_key: str):
    """Lazily import and build an OpenAI client."""
    try:
        from openai import OpenAI
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="OpenAI Python package is not installed. Run: pip install openai",
        )
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="No OpenAI API key configured. Go to Settings and add your API key.",
        )
    return OpenAI(api_key=api_key)


def _is_openai_quota_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "429" in msg or "rate_limit" in msg or "quota" in msg or "insufficient_quota" in msg


# ── Text generation ─────────────────────────────────────────────────────────

async def generate_openai(prompt: str, api_key: str) -> str:
    """Call the OpenAI chat completions endpoint with retries."""
    client = _get_openai_client(api_key)
    last_exc = None

    for attempt in range(_MAX_RETRIES):
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=_OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_exc = e
            if _is_openai_quota_error(e) and attempt < _MAX_RETRIES - 1:
                delay = _BASE_DELAY * (2 ** attempt)
                logger.warning(
                    f"OpenAI rate-limit on {_OPENAI_MODEL} (attempt {attempt + 1}), "
                    f"retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
            elif not _is_openai_quota_error(e):
                raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")

    if _is_openai_quota_error(last_exc):
        raise HTTPException(
            status_code=429,
            detail=(
                "OpenAI API quota exceeded. Check your billing at "
                "https://platform.openai.com/account/billing or try again later."
            ),
        )
    raise HTTPException(status_code=500, detail=f"OpenAI error: {str(last_exc)}")


# ── Embeddings ───────────────────────────────────────────────────────────────

def embed_text_openai(text: str, api_key: str) -> list[float]:
    """Generate an embedding using OpenAI text-embedding-3-small."""
    client = _get_openai_client(api_key)
    response = client.embeddings.create(
        model=_OPENAI_EMBEDDING_MODEL,
        input=text[:8000],
    )
    return list(response.data[0].embedding)
