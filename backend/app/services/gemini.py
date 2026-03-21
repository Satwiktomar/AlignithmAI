from google import genai
import os
import json
import re
import asyncio
import hashlib
import logging
from dotenv import load_dotenv
from fastapi import HTTPException
from app.services.ollama_service import generate_local, is_ollama_available

load_dotenv()

logger = logging.getLogger(__name__)

_PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.0-flash-lite")
_MAX_RETRIES = 3
_BASE_DELAY = 2


def _get_client(user_api_key: str = None) -> genai.Client:
    if not user_api_key:
        raise HTTPException(
            status_code=400,
            detail="No Gemini API key configured. Go to Settings and add your API key to use AI features."
        )
    return genai.Client(api_key=user_api_key)


EMBEDDING_MODEL = "text-embedding-004"


# ── Provider-aware helpers ──────────────────────────────────────────────────

def get_ai_config(user) -> tuple[str | None, str]:
    """Return (decrypted_api_key, provider) based on the user's settings.

    Centralises the key-decryption + provider lookup so every route can
    call ``key, provider = get_ai_config(current_user)`` instead of
    manually decrypting and passing the provider string.
    """
    from app.services.auth import decrypt_api_key

    provider = getattr(user, "ai_provider", "gemini") or "gemini"
    if provider == "openai":
        return decrypt_api_key(getattr(user, "openai_api_key", None)), "openai"
    return decrypt_api_key(getattr(user, "gemini_api_key", None)), "gemini"


# ── Embeddings ──────────────────────────────────────────────────────────────

def embed_text(text: str, user_api_key: str = None, provider: str = "gemini") -> list[float]:
    """Generate embedding for a text.

    Dispatches to Gemini or OpenAI based on *provider*.
    Returns the embedding vector as a plain Python list of floats.
    """
    if provider == "openai":
        from app.services.openai_service import embed_text_openai
        return embed_text_openai(text, api_key=user_api_key)

    client = _get_client(user_api_key)
    try:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text[:8000],  # guard against overly long input
        )
        return list(response.embeddings[0].values)
    except Exception as e:
        logger.warning(f"Primary embedding failed ({str(e)}), trying fallback embedding-001...")
        response = client.models.embed_content(
            model="models/text-embedding-004", # Some older keys require the 'models/' prefix
            contents=text[:8000]
        )
        return list(response.embeddings[0].values)


def extract_json(text: str) -> dict | list:
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    # Try to fix truncated JSON (common with local models)
    match = re.search(r"(\{[\s\S]*)", text)
    if match:
        fragment = match.group(1)
        # Strip trailing incomplete values
        fragment = re.sub(r',\s*"[^"]*$', '', fragment)
        fragment = re.sub(r',\s*$', '', fragment)
        # Count and close unclosed braces/brackets
        opens = fragment.count('{') - fragment.count('}')
        open_b = fragment.count('[') - fragment.count(']')
        fragment += ']' * max(open_b, 0)
        fragment += '}' * max(opens, 0)
        try:
            return json.loads(fragment)
        except Exception:
            pass
    return {"error": "Could not parse response", "raw": text[:500]}


def _is_quota_error(exc: Exception) -> bool:
    return "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc) or "quota" in str(exc).lower()


async def _call_with_retry(client, model: str, prompt: str) -> str:
    last_exc = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = await client.aio.models.generate_content(
                model=model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            last_exc = e
            if _is_quota_error(e) and attempt < _MAX_RETRIES - 1:
                delay = _BASE_DELAY * (2 ** attempt)
                logger.warning(f"Gemini quota hit on {model} (attempt {attempt + 1}), retrying in {delay}s...")
                await asyncio.sleep(delay)
            elif not _is_quota_error(e):
                raise e
    raise last_exc


async def _try_local_fallback(prompt: str) -> str:
    if not await is_ollama_available():
        raise HTTPException(
            status_code=503,
            detail="Local AI model (Ollama) is not running. Start Ollama or switch to Cloud AI."
        )
    try:
        logger.info("Using local Ollama model as fallback")
        return await generate_local(prompt)
    except Exception as local_err:
        raise HTTPException(status_code=500, detail=f"Local model error: {str(local_err)}")


async def generate(
    prompt: str,
    user_api_key: str = None,
    use_local_model: bool = False,
    provider: str = "gemini",
    use_cache: bool = False,
    cache_user_id: int = None,
    cache_db=None,
) -> str:
    # ── Prompt-level cache lookup ────────────────────────────────────
    if use_cache and cache_db is not None and cache_user_id is not None:
        cache_key = hashlib.sha256(prompt.encode()).hexdigest()
        from app.models import CachedRoadmap
        cached = cache_db.query(CachedRoadmap).filter(
            CachedRoadmap.user_id == cache_user_id,
            CachedRoadmap.topic_key == cache_key,
        ).first()
        if cached:
            logger.info(f"Prompt cache HIT (key={cache_key[:12]}…)")
            return json.dumps(cached.result_json) if isinstance(cached.result_json, (dict, list)) else str(cached.result_json)

    if use_local_model:
        return await _try_local_fallback(prompt)

    # ── OpenAI provider path ─────────────────────────────────────────
    if provider == "openai":
        if not user_api_key:
            if await is_ollama_available():
                logger.info("No OpenAI key — falling back to local Ollama model")
                return await _try_local_fallback(prompt)
            raise HTTPException(
                status_code=400,
                detail="No OpenAI API key configured. Go to Settings and add your API key, or enable Local AI.",
            )
        from app.services.openai_service import generate_openai
        return await generate_openai(prompt, api_key=user_api_key)

    # ── Gemini provider path (default) ───────────────────────────────
    if not user_api_key:
        if await is_ollama_available():
            logger.info("No API key — falling back to local Ollama model")
            return await _try_local_fallback(prompt)
        raise HTTPException(
            status_code=400,
            detail="No Gemini API key configured. Go to Settings and add your API key, or enable Local AI."
        )

    client = _get_client(user_api_key)

    try:
        return await _call_with_retry(client, _PRIMARY_MODEL, prompt)
    except Exception as e:
        if not _is_quota_error(e):
            raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")

    try:
        return await _call_with_retry(client, _FALLBACK_MODEL, prompt)
    except Exception as e:
        if _is_quota_error(e):
            logger.warning("Gemini quota exhausted on both models, trying local Ollama fallback...")
            try:
                return await _try_local_fallback(prompt)
            except Exception:
                raise HTTPException(
                    status_code=429,
                    detail=(
                        "Gemini API quota exceeded on both models and local AI is unavailable. "
                        "Note: Multiple API keys from the same Google Cloud project share the "
                        "same quota — a different key won't help. "
                        "Try adding an OpenAI key in Settings as an alternative provider, "
                        "or wait a few minutes and try again."
                    ),
                )
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")


async def generate_cached(
    prompt: str,
    user_api_key: str = None,
    use_local_model: bool = False,
    provider: str = "gemini",
    cache_user_id: int = None,
    cache_db=None,
) -> str:
    """generate() with prompt caching enabled. Stores successful results."""
    cache_key = hashlib.sha256(prompt.encode()).hexdigest()

    # Check cache first
    if cache_db is not None and cache_user_id is not None:
        from app.models import CachedRoadmap
        cached = cache_db.query(CachedRoadmap).filter(
            CachedRoadmap.user_id == cache_user_id,
            CachedRoadmap.topic_key == cache_key,
        ).first()
        if cached:
            logger.info(f"Prompt cache HIT (key={cache_key[:12]}…)")
            return json.dumps(cached.result_json) if isinstance(cached.result_json, (dict, list)) else str(cached.result_json)

    # Call AI normally
    result_text = await generate(prompt, user_api_key=user_api_key, use_local_model=use_local_model, provider=provider)

    # Store in cache
    if cache_db is not None and cache_user_id is not None:
        try:
            from app.models import CachedRoadmap
            parsed = extract_json(result_text)
            if isinstance(parsed, (dict, list)) and not (isinstance(parsed, dict) and parsed.get("error")):
                entry = CachedRoadmap(
                    user_id=cache_user_id,
                    topic_key=cache_key,
                    topic_display=f"cached_prompt_{cache_key[:16]}",
                    result_json=parsed,
                )
                cache_db.add(entry)
                cache_db.commit()
                logger.info(f"Prompt cache STORE (key={cache_key[:12]}…)")
        except Exception as e:
            logger.warning(f"Failed to cache prompt result: {e}")

    return result_text


async def generate_json(
    prompt: str,
    user_api_key: str = None,
    use_local_model: bool = False,
    provider: str = "gemini",
) -> dict | list:
    text = await generate(prompt, user_api_key, use_local_model, provider=provider)
    return extract_json(text)


generate_text = generate
