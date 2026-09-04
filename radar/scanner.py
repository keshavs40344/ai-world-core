"""
radar/scanner.py
================
RADAR Controller — Step 1: Trend Scanning.

Fetches live popularity signals from three public sources:
  1. PyPI Stats API   — download counts for top packages
  2. GitHub Topics    — repository counts & trending repos per topic
  3. Hugging Face     — trending Spaces (HTML scrape)

All requests respect robots.txt and enforce a per-request rate-limit
defined in config.RADAR_RATE_LIMIT_SEC. External failures are caught
and logged; the scanner returns whatever partial data it collects.
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from typing import Any
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from genesis import config

log = logging.getLogger("radar.scanner")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TrendSignal:
    source: str                     # "pypi" | "github" | "huggingface"
    name: str                       # package / repo / space name
    description: str = ""
    url: str = ""
    score: float = 0.0              # normalised popularity score 0–1
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# robots.txt check
# ---------------------------------------------------------------------------

_robots_cache: dict[str, RobotFileParser] = {}

def _can_fetch(url: str, user_agent: str = "*") -> bool:
    """Return True if robots.txt allows fetching the URL."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    if base not in _robots_cache:
        rp = RobotFileParser()
        try:
            rp.set_url(f"{base}/robots.txt")
            rp.read()
        except Exception:
            rp = RobotFileParser()   # allow-all fallback
        _robots_cache[base] = rp
    return _robots_cache[base].can_fetch(user_agent, url)


# ---------------------------------------------------------------------------
# Shared HTTP client
# ---------------------------------------------------------------------------

_HEADERS = {
    "User-Agent": "GenesisRADAR/1.0 (open-source research bot; github.com/genesis)",
    "Accept": "application/json",
}

def _get(client: httpx.Client, url: str, **kwargs) -> httpx.Response | None:
    """Rate-limited, robots-respecting GET request."""
    if not _can_fetch(url):
        log.warning(f"robots.txt disallows fetching {url} — skipping.")
        return None
    time.sleep(config.RADAR_RATE_LIMIT_SEC)
    try:
        resp = client.get(url, headers=_HEADERS, timeout=15.0, **kwargs)
        resp.raise_for_status()
        return resp
    except Exception as exc:
        log.warning(f"GET {url} failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Source: PyPI Stats
# ---------------------------------------------------------------------------

def _scan_pypi(client: httpx.Client, top_n: int) -> list[TrendSignal]:
    """
    Query pypistats.org for the top downloaded Python packages.
    Returns the top_n by recent download count as TrendSignals.
    """
    signals: list[TrendSignal] = []

    # PyPI top packages (unofficial but widely used)
    url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
    resp = _get(client, url)
    if resp is None:
        return signals

    try:
        data = resp.json()
        rows = data.get("rows", [])[:top_n]
        max_downloads = rows[0]["download_count"] if rows else 1

        for row in rows:
            name = row["project"]
            count = row["download_count"]
            score = count / max_downloads

            # Fetch package metadata from PyPI JSON API
            meta_resp = _get(client, f"https://pypi.org/pypi/{name}/json")
            description = ""
            tags: list[str] = []
            if meta_resp:
                meta = meta_resp.json()
                info = meta.get("info", {})
                description = info.get("summary", "")
                tags = [
                    kw.strip()
                    for kw in (info.get("keywords") or "").split(",")
                    if kw.strip()
                ]

            signals.append(TrendSignal(
                source="pypi",
                name=name,
                description=description,
                url=f"https://pypi.org/project/{name}/",
                score=score,
                tags=tags,
                metadata={"downloads_30d": count},
            ))

    except Exception as exc:
        log.warning(f"PyPI scan parse error: {exc}")

    log.info(f"[RADAR/PyPI] {len(signals)} signals collected.")
    return signals


# ---------------------------------------------------------------------------
# Source: GitHub Topics
# ---------------------------------------------------------------------------

def _scan_github_topics(client: httpx.Client) -> list[TrendSignal]:
    """
    Use the GitHub REST API (unauthenticated) to count repos per topic
    and fetch a sample of trending repositories.
    """
    signals: list[TrendSignal] = []

    for topic in config.RADAR_GITHUB_TOPICS:
        url = f"https://api.github.com/search/repositories"
        params = {
            "q": f"topic:{topic}",
            "sort": "stars",
            "order": "desc",
            "per_page": 10,
        }
        resp = _get(client, url, params=params)
        if resp is None:
            continue

        try:
            data = resp.json()
            total = data.get("total_count", 0)
            items = data.get("items", [])
            max_stars = items[0]["stargazers_count"] if items else 1

            for item in items:
                stars = item.get("stargazers_count", 0)
                signals.append(TrendSignal(
                    source="github",
                    name=item.get("full_name", ""),
                    description=item.get("description", "") or "",
                    url=item.get("html_url", ""),
                    score=stars / max(max_stars, 1),
                    tags=[topic] + item.get("topics", []),
                    metadata={
                        "stars": stars,
                        "forks": item.get("forks_count", 0),
                        "language": item.get("language", ""),
                        "topic_total_repos": total,
                    },
                ))
        except Exception as exc:
            log.warning(f"GitHub topic '{topic}' parse error: {exc}")

    log.info(f"[RADAR/GitHub] {len(signals)} signals collected.")
    return signals


# ---------------------------------------------------------------------------
# Source: Hugging Face Trending Spaces
# ---------------------------------------------------------------------------

def _scan_huggingface(client: httpx.Client) -> list[TrendSignal]:
    """
    Scrape the HuggingFace Spaces trending page (public, no auth required).
    Extracts space names, descriptions, and like counts.
    """
    signals: list[TrendSignal] = []
    url = "https://huggingface.co/spaces?sort=trending"

    resp = _get(client, url)
    if resp is None:
        return signals

    # HuggingFace also offers a public API
    api_url = "https://huggingface.co/api/spaces?sort=trending&limit=20"
    api_resp = _get(client, api_url)
    if api_resp:
        try:
            items = api_resp.json()
            max_likes = max((i.get("likes", 0) for i in items), default=1)
            for item in items:
                likes = item.get("likes", 0)
                signals.append(TrendSignal(
                    source="huggingface",
                    name=item.get("id", ""),
                    description=item.get("cardData", {}).get("short_description", ""),
                    url=f"https://huggingface.co/spaces/{item.get('id', '')}",
                    score=likes / max(max_likes, 1),
                    tags=item.get("tags", []),
                    metadata={"likes": likes, "sdk": item.get("sdk", "")},
                ))
        except Exception as exc:
            log.warning(f"HuggingFace API parse error: {exc}")
    else:
        # Fallback: HTML scrape
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            for card in soup.select("article")[:20]:
                name_el = card.select_one("h4")
                desc_el = card.select_one("p")
                link_el = card.select_one("a[href*='/spaces/']")
                if name_el:
                    signals.append(TrendSignal(
                        source="huggingface",
                        name=name_el.get_text(strip=True),
                        description=desc_el.get_text(strip=True) if desc_el else "",
                        url=f"https://huggingface.co{link_el['href']}" if link_el else "",
                        score=0.5,
                    ))
        except Exception as exc:
            log.warning(f"HuggingFace HTML scrape error: {exc}")

    log.info(f"[RADAR/HuggingFace] {len(signals)} signals collected.")
    return signals


# ---------------------------------------------------------------------------
# Main scanner class
# ---------------------------------------------------------------------------

class RadarScanner:
    """
    Aggregates trend signals from PyPI, GitHub, and HuggingFace.

    Returns a flat list of TrendSignal objects sorted by score descending.
    Gracefully handles individual source failures — partial results are
    always returned.
    """

    def scan(self) -> list[TrendSignal]:
        signals: list[TrendSignal] = []

        with httpx.Client(follow_redirects=True) as client:
            # PyPI
            try:
                signals.extend(_scan_pypi(client, top_n=config.RADAR_PYPI_TOP_N))
            except Exception as exc:
                log.error(f"PyPI scan failed: {exc}")

            # GitHub
            try:
                signals.extend(_scan_github_topics(client))
            except Exception as exc:
                log.error(f"GitHub scan failed: {exc}")

            # HuggingFace
            try:
                signals.extend(_scan_huggingface(client))
            except Exception as exc:
                log.error(f"HuggingFace scan failed: {exc}")

        # Sort by score descending
        signals.sort(key=lambda s: s.score, reverse=True)
        log.info(f"[RADAR] Total signals: {len(signals)}")
        return signals
