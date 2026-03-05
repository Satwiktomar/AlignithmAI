from google import genai
import os
import json
import re
import asyncio
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


async def generate(prompt: str, user_api_key: str = None, use_local_model: bool = False) -> str:
    if use_local_model:
        return await _try_local_fallback(prompt)

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
                    detail="Gemini API quota exceeded and local AI is unavailable. Please wait and try again."
                )
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")


async def generate_json(prompt: str, user_api_key: str = None, use_local_model: bool = False) -> dict | list:
    text = await generate(prompt, user_api_key, use_local_model)
    return extract_json(text)


generate_text = generate

