import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

_PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")

model = genai.GenerativeModel(_PRIMARY_MODEL)
fallback_model = genai.GenerativeModel(_FALLBACK_MODEL)


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
    return {"error": "Could not parse response", "raw": text}


def _is_quota_error(exc: Exception) -> bool:
    return "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc) or "quota" in str(exc).lower()


async def generate(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if not _is_quota_error(e):
            raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")

    try:
        response = fallback_model.generate_content(prompt)
        return response.text
    except Exception as e:
        if _is_quota_error(e):
            raise HTTPException(
                status_code=429,
                detail=(
                    "⚠️ Gemini API daily quota exceeded on all models. "
                    "Please wait a few minutes and try again, or add billing at "
                    "https://ai.google.dev to increase your quota."
                )
            )
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")


async def generate_json(prompt: str) -> dict | list:
    text = await generate(prompt)
    return extract_json(text)


generate_text = generate
