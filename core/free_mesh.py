"""
VASTUDA Sovereign Core — Free Resource Mesh (free_mesh.py)
Aggregates 100% free, zero-key, and public APIs:
1. DuckDuckGo (Web search & instant answers, zero key)
2. Wikipedia (Encyclopedic knowledge & deep definitions, zero key)
3. HackerNews (Real developer sentiment, trending SaaS launches, zero key)
4. GitHub Public API (Open-source architecture patterns & trends, zero key)
5. Pollinations AI (Zero-key generative visuals and media assets)
"""

import os
import sys
import json
import time
import re
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

# UTF-8 stdout setup
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

class FreeResourceMesh:
    """Consolidated gateway to zero-key public data resources."""

    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

    # ─────────────────────────────────────────────────────────────
    # 1. DUCKDUCKGO (ZERO KEY)
    # ─────────────────────────────────────────────────────────────
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Performs live web search via DuckDuckGo without any API key."""
        results = []
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                matches = re.findall(r'<a class="result__snippet[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html)
                titles = re.findall(r'<a class="result__url[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html)

                for i, (link, snippet) in enumerate(matches[:max_results]):
                    clean_snip = re.sub(r'<[^>]+>', '', snippet).strip()
                    title = query
                    if i < len(titles):
                        clean_title = re.sub(r'<[^>]+>', '', titles[i][1]).strip()
                        if clean_title:
                            title = clean_title
                    results.append({
                        "source": "DuckDuckGo",
                        "title": title,
                        "snippet": clean_snip,
                        "url": link
                    })
        except Exception:
            pass

        return results

    # ─────────────────────────────────────────────────────────────
    # 2. WIKIPEDIA REST API (ZERO KEY)
    # ─────────────────────────────────────────────────────────────
    def search_wikipedia(self, topic: str) -> Optional[Dict[str, Any]]:
        """Fetches authoritative structured summary from Wikipedia REST API."""
        try:
            clean_topic = urllib.parse.quote(topic.replace(" ", "_"))
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_topic}"
            req = urllib.request.Request(url, headers={"User-Agent": "VastudaSovereignMesh/2.0 (contact@vastuda.ai)"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {
                    "source": "Wikipedia",
                    "title": data.get("title", topic),
                    "extract": data.get("extract", ""),
                    "description": data.get("description", ""),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                }
        except Exception:
            return None

    # ─────────────────────────────────────────────────────────────
    # 3. HACKER NEWS PUBLIC API (ZERO KEY)
    # ─────────────────────────────────────────────────────────────
    def search_hackernews(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries Algolia HN Search API for real developer sentiment and expensive SaaS discussions."""
        results = []
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://hn.algolia.com/api/v1/search?query={encoded}&tags=story&hitsPerPage={limit}"
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for hit in data.get("hits", []):
                    results.append({
                        "source": "HackerNews",
                        "title": hit.get("title", ""),
                        "points": hit.get("points", 0),
                        "num_comments": hit.get("num_comments", 0),
                        "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID')}")
                    })
        except Exception:
            pass
        return results

    # ─────────────────────────────────────────────────────────────
    # 4. GITHUB PUBLIC API (ZERO KEY)
    # ─────────────────────────────────────────────────────────────
    def search_github_repositories(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Searches GitHub public repositories for architectural patterns and benchmarks."""
        results = []
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc&per_page={limit}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "VastudaSovereignMesh",
                "Accept": "application/vnd.github.v3+json"
            })
            with urllib.request.urlopen(req, timeout=7) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for repo in data.get("items", []):
                    results.append({
                        "source": "GitHub",
                        "name": repo.get("full_name", ""),
                        "description": repo.get("description", "") or "",
                        "stars": repo.get("stargazers_count", 0),
                        "url": repo.get("html_url", "")
                    })
        except Exception:
            pass
        return results

    # ─────────────────────────────────────────────────────────────
    # 5. POLLINATIONS AI VISUAL GENERATOR (ZERO KEY)
    # ─────────────────────────────────────────────────────────────
    def generate_visual_asset_url(self, prompt: str, width: int = 1200, height: int = 630) -> str:
        """Generates dynamic visual banner URL using Pollinations AI (100% free, zero key)."""
        clean_prompt = urllib.parse.quote(prompt[:120])
        return f"https://image.pollinations.ai/prompt/{clean_prompt}?width={width}&height={height}&nologo=true"

    # ─────────────────────────────────────────────────────────────
    # UNIFIED SCOUT HARVESTER
    # ─────────────────────────────────────────────────────────────
    def harvest_target_intelligence(self, target_topic: str) -> Dict[str, Any]:
        """Gathers multi-source intelligence across DuckDuckGo, Wikipedia, HackerNews, and GitHub."""
        web_signals = self.search_duckduckgo(f"{target_topic} pricing alternative expensive", max_results=3)
        wiki_data = self.search_wikipedia(target_topic)
        hn_discussions = self.search_hackernews(f"{target_topic} alternative", limit=3)
        gh_repos = self.search_github_repositories(f"{target_topic} tool", limit=3)

        return {
            "target": target_topic,
            "web_signals": web_signals,
            "wikipedia": wiki_data,
            "hackernews": hn_discussions,
            "github_benchmarks": gh_repos,
            "banner_url": self.generate_visual_asset_url(f"futuristic cybernetic dashboard interface for {target_topic}")
        }

if __name__ == "__main__":
    mesh = FreeResourceMesh()
    print("Testing Free Resource Mesh...")
    intel = mesh.harvest_target_intelligence("SEO Audit")
    print(f"Web signals harvested: {len(intel['web_signals'])}")
    print(f"HN discussions found: {len(intel['hackernews'])}")
    print(f"GitHub benchmarks: {len(intel['github_benchmarks'])}")
    print(f"Visual asset URL: {intel['banner_url']}")
