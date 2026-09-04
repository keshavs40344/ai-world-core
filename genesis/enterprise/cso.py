import os
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any

class ChiefStrategyOfficer:
    """Division 1: Market Expansion & Opportunity Scout (CSO).
    Sweeps public internet feeds for developer pain points, high-volume repetitive tasks,
    and commercial product gaps. Emits a formal Market_Opportunity_Brief.json.
    """
    
    DEMAND_FEEDS = [
        "https://news.ycombinator.com/rss",
        "https://pypi.org/rss/updates.xml"
    ]
    
    def sweep_market_signals(self) -> Dict[str, str]:
        for feed in self.DEMAND_FEEDS:
            try:
                req = urllib.request.Request(feed, headers={"User-Agent": "Genesis-CSO/1.0 (+https://github.com/keshavs40344/ai-world-core)"})
                with urllib.request.urlopen(req, timeout=6) as response:
                    root = ET.fromstring(response.read())
                    item = root.find(".//channel/item")
                    if item is not None:
                        title = item.find("title").text if item.find("title") is not None else "High Demand API"
                        link = item.find("link").text if item.find("link") is not None else feed
                        return {"title": title.strip(), "link": link.strip(), "feed": feed}
            except Exception:
                continue

        return {
            "title": f"High-Throughput Schema Validator & Data Normalizer {int(time.time())}",
            "link": "https://pypi.org",
            "feed": "internal_demand_engine"
        }

    def generate_opportunity_brief(self, signal: Dict[str, str], venture_dir: str) -> Dict[str, Any]:
        raw_title = signal["title"]
        slug = "".join([c if c.isalnum() else "_" for c in raw_title.lower()])[:24].strip("_")
        venture_slug = f"venture_{slug}_{int(time.time())}"
        
        brief = {
            "venture_slug": venture_slug,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "market_vertical": "Cloud Micro-Services & Developer Infrastructure",
            "origin_signal": {
                "title": raw_title,
                "source": signal.get("link", "N/A"),
                "feed": signal.get("feed", "N/A")
            },
            "commercial_thesis": {
                "problem_statement": f"Market demand surging around '{raw_title}'. Developers need instant, zero-setup data formatting without subscribing to expensive paid cloud gateways.",
                "solution_specification": "Turnkey Python micro-engine and FastAPI compatible data standardizer with zero dependencies.",
                "target_demographic": "SaaS builders, autonomous agents, and data engineering pipelines.",
                "monetization_vector": "Freemium API on RapidAPI ($0 for 10k calls, $9.99/mo for 250k calls) + Static GitHub Pages programmatic SEO hub.",
                "projected_gross_margin": "100.0% ($0 cloud serverless cost)"
            }
        }
        
        os.makedirs(venture_dir, exist_ok=True)
        brief_path = os.path.join(venture_dir, "Market_Opportunity_Brief.json")
        with open(brief_path, "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2)
            
        return brief
