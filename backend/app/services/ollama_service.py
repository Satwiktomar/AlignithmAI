import os
import json
import re
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


async def is_ollama_available() -> bool:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def get_ollama_status() -> dict:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                return {
                    "available": True,
                    "model": OLLAMA_MODEL,
                    "installed_models": models,
                    "model_ready": any(OLLAMA_MODEL in m for m in models)
                }
    except Exception:
        pass
    return {"available": False, "model": OLLAMA_MODEL, "installed_models": [], "model_ready": False}


def _extract_json(text: str) -> dict | list:
    import json
    import re
    
    # 1. Try raw text
    try:
        return json.loads(text)
    except Exception:
        pass
        
    # 2. Try markdown code blocks
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
            
    # 3. Clean string and try bracket counting
    # Sometimes trailing text contains braces, so we find the first { or [
    start_idx = -1
    for i, c in enumerate(text):
        if c in ('{', '['):
            start_idx = i
            break
            
    if start_idx != -1:
        is_array = text[start_idx] == '['
        open_char = '[' if is_array else '{'
        close_char = ']' if is_array else '}'
        
        count = 0
        end_idx = -1
        in_string = False
        escape = False
        
        for i in range(start_idx, len(text)):
            c = text[i]
            if escape:
                escape = False
                continue
            if c == '\\':
                escape = True
                continue
            if c == '"':
                in_string = not in_string
                continue
                
            if not in_string:
                if c == open_char:
                    count += 1
                elif c == close_char:
                    count -= 1
                    if count == 0:
                        end_idx = i
                        break
                        
        if end_idx != -1:
            try:
                candidate = text[start_idx:end_idx+1]
                return json.loads(candidate)
            except Exception:
                pass

    # 4. Fallback for truncated JSON (naive)
    match = re.search(r"(\{[\s\S]*)", text)
    if match:
        fragment = match.group(1)
        fragment = re.sub(r',\s*"[^"]*$', '', fragment)
        fragment = re.sub(r',\s*$', '', fragment)
        opens = fragment.count('{') - fragment.count('}')
        open_b = fragment.count('[') - fragment.count(']')
        fragment += ']' * max(open_b, 0)
        fragment += '}' * max(opens, 0)
        try:
            return json.loads(fragment)
        except Exception:
            pass

    return {"error": "Could not parse local model response", "raw": text[:500]}


async def generate_local(prompt: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            r = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 8192}
                }
            )
            if r.status_code == 200:
                return r.json().get("response", "")
            raise Exception(f"Ollama returned status {r.status_code}: {r.text}")
    except httpx.TimeoutException:
        raise Exception("Local model timed out. The model may still be loading.")
    except httpx.ConnectError:
        raise Exception("Ollama is not running. Start it with 'ollama serve' or launch the Ollama app.")


async def generate_local_json(prompt: str) -> dict | list:
    text = await generate_local(prompt)
    return _extract_json(text)
