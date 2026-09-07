"""
VASTUDA Swarm — Agent Scout (Market Hunter)
Scouts the internet using FreeResourceMesh (DuckDuckGo, HackerNews, GitHub).
Identifies commercial SaaS products that charge heavy recurring subscriptions ($20-$100/mo).
Generates an actionable Target Dossier for the Diagnostician and Builder.
"""

import os
import sys
import json
import random
from typing import Dict, Any, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.agent_brain import AgentBrain
from core.free_mesh import FreeResourceMesh
from core.training_engine import SwarmTrainingEngine

# Curated benchmark of expensive commercial SaaS niches ripe for disruption
HIGH_CHARGE_NICHES = [
    {
        "niche": "Technical & On-Page SEO Diagnostics",
        "benchmark_app": "Ahrefs Site Audit / SEMrush On-Page",
        "monthly_charge": "$129/mo",
        "pain_points": "Heavily paywalled, credit limits, forced enterprise tiers."
    },
    {
        "niche": "Visual Stock Health & DCF Intrinsic Valuation",
        "benchmark_app": "Simply Wall St / Koyfin Basic",
        "monthly_charge": "$39/mo",
        "pain_points": "Restricted stock checks per month, delayed data, expensive annual lock-ins."
    },
    {
        "niche": "Professional Vector Invoice & Quote Generator",
        "benchmark_app": "FreshBooks / Invoice Simple Pro",
        "monthly_charge": "$19/mo",
        "pain_points": "Annoying watermarks, forced user logins, client limit caps."
    },
    {
        "niche": "Real-Time Social Card & OG-Image Designer",
        "benchmark_app": "Canva Pro / BrandKit",
        "monthly_charge": "$15/mo",
        "pain_points": "Paywalled export formats, watermarked templates, cloud storage limits."
    },
    {
        "niche": "REST API Inspector & Mock Response Engine",
        "benchmark_app": "Postman Team Plan",
        "monthly_charge": "$29/mo",
        "pain_points": "Requires account login, cloud sync privacy concerns for internal endpoints."
    },
    {
        "niche": "Client-Side High-Resolution Image Compressor",
        "benchmark_app": "TinyPNG Pro / Kraken.io",
        "monthly_charge": "$25/mo",
        "pain_points": "Monthly image quota limits, server uploads of private confidential graphics."
    }
]

class AgentScout:
    def __init__(self, brain: Optional[AgentBrain] = None, mesh: Optional[FreeResourceMesh] = None, trainer: Optional[SwarmTrainingEngine] = None):
        self.brain = brain or AgentBrain()
        self.mesh = mesh or FreeResourceMesh()
        self.trainer = trainer or SwarmTrainingEngine()

    def scout_next_target(self, existing_slugs: List[str]) -> Dict[str, Any]:
        """Identifies a prime expensive SaaS target using live web intelligence."""
        # Check training weights to avoid repeated niches
        training_adapters = self.trainer.get_trained_prompt_adapters("Scout")

        # Pick candidate niche
        candidate = random.choice(HIGH_CHARGE_NICHES)

        # Harvest real web intelligence
        print(f"  [Scout] Harvesting free web signals for: {candidate['niche']}...")
        intel = self.mesh.harvest_target_intelligence(candidate["niche"])

        prompt = f"""
You are Agent Scout, the Market Intelligence Hunter of the VASTUDA Swarm.
Your mandate: Identify an expensive SaaS tool charging $20-$120/mo and build a Target Dossier for our Builder to disrupt.

Niche Candidate: {candidate['niche']}
Commercial Benchmark: {candidate['benchmark_app']} ({candidate['monthly_charge']})
Known User Frustrations: {candidate['pain_points']}

Live Web Signals:
{json.dumps(intel.get('web_signals', [])[:2])}

{training_adapters}

Respond ONLY with valid JSON:
{{
  "target_name": "{candidate['benchmark_app']}",
  "niche": "{candidate['niche']}",
  "typical_price": "{candidate['monthly_charge']}",
  "user_pain_points": "{candidate['pain_points']}",
  "disruptive_opportunity": "How our 100% free client-side app will completely outperform it",
  "recommended_app_title": "Clean, authoritative title of our superior free alternative",
  "app_slug": "clean_snake_case_slug",
  "key_features_to_include": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"]
}}
"""
        dossier = self.brain.think_structured(prompt, system_prompt="You are an expert SaaS market intelligence researcher. Always output valid JSON.")

        # Fallback if structure failed
        if "app_slug" not in dossier or "recommended_app_title" not in dossier:
            slug = candidate["niche"].lower().replace(" ", "_").replace("&", "").replace("-", "_")[:30]
            dossier = {
                "target_name": candidate["benchmark_app"],
                "niche": candidate["niche"],
                "typical_price": candidate["monthly_charge"],
                "user_pain_points": candidate["pain_points"],
                "disruptive_opportunity": "Deliver a 100% free client-side app with zero paywalls and zero signups.",
                "recommended_app_title": f"Sovereign {candidate['niche']} Studio",
                "app_slug": slug,
                "key_features_to_include": ["Interactive Controls", "Live Visual Calculations", "Instant Export", "Zero Paywall"]
            }

        dossier["web_intel"] = intel
        return dossier

if __name__ == "__main__":
    scout = AgentScout()
    dossier = scout.scout_next_target([])
    print("Scout Target Dossier:")
    print(json.dumps(dossier, indent=2))
