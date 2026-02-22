import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException


async def scrape_job_url(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            response = await client.get(url, headers=headers)
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=400,
            detail="URL request timed out. Please paste the job description text directly."
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not reach URL: {str(e)}. Please paste the job description text directly."
        )

    if response.status_code in (403, 401, 429):
        raise HTTPException(
            status_code=400,
            detail=(
                f"This job site blocked scraping (HTTP {response.status_code} — {url}). "
                "Please open the job posting and paste the description text directly."
            )
        )

    try:
        response.raise_for_status()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"URL returned HTTP {response.status_code}. Please paste the job description text directly."
        )

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
        tag.decompose()

    job_section = (
        soup.find("div", {"class": lambda c: c and any(k in c.lower() for k in ["job", "description", "posting", "content", "detail"])})
        or soup.find("article")
        or soup.find("main")
        or soup.body
    )

    raw_text = job_section.get_text(separator="\n", strip=True) if job_section else soup.get_text(separator="\n", strip=True)

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    text = "\n".join(lines[:800])

    if len(text) < 100:
        raise HTTPException(
            status_code=400,
            detail="Could not extract meaningful content from URL. Please paste the job description text directly."
        )

    return text
