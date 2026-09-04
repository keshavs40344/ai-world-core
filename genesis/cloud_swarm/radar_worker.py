import time
import random
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

class RadarWorker:
    """Radar Worker: Public RSS Scraper & Tech Signal Scout.
    Runs in cloud runners with zero local compute footprint.
    Strictly white-hat: Respects rate limits with randomized jitter, public endpoints only.
    """
    
    USER_AGENT = "Mozilla/5.0 (compatible; GenesisDefensiveScout/1.0; +https://github.com/keshavs40344/ai-world-core)"
    FEEDS = [
        "https://news.ycombinator.com/rss",
        "https://pypi.org/rss/updates.xml"
    ]

    def __init__(self, jitter_min: float = 0.5, jitter_max: float = 1.2):
        self.jitter_min = jitter_min
        self.jitter_max = jitter_max

    def scout_signal(self) -> Dict[str, Any]:
        """Scout unauthenticated public tech signals with courteous jitter."""
        # Courteous randomized delay to respect remote rate limits
        jitter = random.uniform(self.jitter_min, self.jitter_max)
        time.sleep(jitter)
        
        for url in self.FEEDS:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": self.USER_AGENT})
                with urllib.request.urlopen(req, timeout=8) as response:
                    root = ET.fromstring(response.read())
                    item = root.find(".//channel/item")
                    if item is not None:
                        title_el = item.find("title")
                        link_el = item.find("link")
                        title = title_el.text.strip() if title_el is not None and title_el.text else "Autonomous Cloud Task"
                        link = link_el.text.strip() if link_el is not None and link_el.text else url
                        return {
                            "source": url,
                            "title": title,
                            "link": link,
                            "jitter_applied_sec": round(jitter, 3),
                            "scout_time": time.time()
                        }
            except Exception:
                continue

        # Deterministic cloud fallback
        return {
            "source": "cloud-internal-synthesizer",
            "title": f"Headless Micro-API Stream Normalizer {int(time.time())}",
            "link": "https://github.com/keshavs40344/ai-world-core",
            "jitter_applied_sec": round(jitter, 3),
            "scout_time": time.time()
        }
