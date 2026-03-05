import httpx
import ipaddress
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

ALLOWED_SCHEMES = {"http", "https"}
MAX_REDIRECTS = 5


def _validate_url(url: str) -> str:
    """Validate URL to prevent SSRF attacks."""
    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are allowed."
        )

    if not parsed.hostname:
        raise HTTPException(status_code=400, detail="Invalid URL: no hostname found.")

    try:
        import socket
        resolved = socket.getaddrinfo(parsed.hostname, None)
        for _, _, _, _, addr in resolved:
            ip = ipaddress.ip_address(addr[0])
            for network in BLOCKED_NETWORKS:
                if ip in network:
                    raise HTTPException(
                        status_code=400,
                        detail="URL points to a private/internal network. Please use a public job posting URL."
                    )
    except HTTPException:
        raise
    except Exception:
        pass

    return url


async def scrape_job_url(url: str) -> str:
    """Scrape job description from URL with SSRF protection."""
    url = _validate_url(url)

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
        async with httpx.AsyncClient(follow_redirects=True, max_redirects=MAX_REDIRECTS, timeout=15) as client:
            response = await client.get(url, headers=headers)
    except httpx.TooManyRedirects:
        raise HTTPException(
            status_code=400,
            detail="URL has too many redirects. Please paste the job description text directly."
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=400,
            detail="URL request timed out. Please paste the job description text directly."
        )
    except Exception as e:
        logger.warning(f"Scraper error for {url}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Could not reach URL. Please paste the job description text directly."
        )

    if response.status_code in (403, 401, 429):
        raise HTTPException(
            status_code=400,
            detail=(
                f"This job site blocked scraping (HTTP {response.status_code}). "
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
