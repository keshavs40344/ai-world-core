"""
VASTUDA Swarm — Agent Diagnostician (Reverse Engineer)
Analyzes expensive SaaS products targeted by Agent Scout.
Deconstructs their UI/UX, data flow, calculation formulas, and architectural bottlenecks.
Produces a rigorous Architectural Blueprint for Agent Builder to construct a superior alternative.
"""

import os
import sys
import json
from typing import Dict, Any, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.agent_brain import AgentBrain
from core.training_engine import SwarmTrainingEngine

class AgentDiagnostician:
    def __init__(self, brain: Optional[AgentBrain] = None, trainer: Optional[SwarmTrainingEngine] = None):
        self.brain = brain or AgentBrain()
        self.trainer = trainer or SwarmTrainingEngine()

    def diagnose_target(self, dossier: Dict[str, Any]) -> Dict[str, Any]:
        """Deconstructs the target product into a detailed technical and UI/UX blueprint."""
        print(f"  [Diagnostician] Reverse-engineering: {dossier.get('target_name')} ({dossier.get('typical_price')})...")
        training_adapters = self.trainer.get_trained_prompt_adapters("Diagnostician")

        prompt = f"""
You are Agent Diagnostician, the Technical Reverse-Engineer of the VASTUDA Swarm.
Target to Reverse-Engineer:
- Product: {dossier.get('target_name')}
- Niche: {dossier.get('niche')}
- Market Subscription: {dossier.get('typical_price')}
- User Pain Points: {dossier.get('user_pain_points')}
- Core Features to replicate & improve: {dossier.get('key_features_to_include')}

{training_adapters}

Task: Design a complete, superior single-page web app architecture that runs 100% client-side with zero paywalls.
Provide exact details on:
1. Input Panel: sliders, file drop, text inputs, toggles.
2. Calculation/Transformation Logic: exact JavaScript algorithms/formulas.
3. Visual Presentation: dark-mode layout, graphs (Chart.js), score cards, tables.
4. Export Suite: copy, download JSON/CSV/PDF, reset.

Respond ONLY with valid JSON matching this schema:
{{
  "app_title": "{dossier.get('recommended_app_title')}",
  "app_slug": "{dossier.get('app_slug')}",
  "ui_layout": "Header with live badges -> Two-column grid (Inputs on left, Live Output on right) -> Export footer",
  "input_controls": [
    {{"name": "Input 1", "type": "number|text|slider|select|textarea", "default": "...", "label": "..."}},
    {{"name": "Input 2", "type": "number|text|slider|select|textarea", "default": "...", "label": "..."}}
  ],
  "core_js_logic": "Step-by-step description of pure JavaScript functions executing the calculations or parsing",
  "visual_cards": ["Metric Card 1", "Metric Card 2", "Visual Canvas/Table"],
  "export_actions": ["Copy to Clipboard", "Download Formatted Result"]
}}
"""
        blueprint = self.brain.think_structured(prompt, system_prompt="You are a senior software architect specializing in client-side web application reverse-engineering.")

        if "app_title" not in blueprint:
            blueprint = {
                "app_title": dossier.get("recommended_app_title", "Sovereign Web App"),
                "app_slug": dossier.get("app_slug", "sovereign_app"),
                "ui_layout": "Modern dual-pane glassmorphism interface with instant reactivity",
                "input_controls": [{"name": "primary_input", "type": "textarea", "default": "", "label": "Configuration"}],
                "core_js_logic": "Pure client-side DOM event listeners recalculating on change",
                "visual_cards": ["Health Metric", "Detailed Breakdown Matrix"],
                "export_actions": ["Copy Output", "Export Data"]
            }

        return blueprint

if __name__ == "__main__":
    diag = AgentDiagnostician()
    sample_dossier = {
        "target_name": "Ahrefs Site Audit ($129/mo)",
        "niche": "Technical SEO",
        "typical_price": "$129/mo",
        "user_pain_points": "Heavy limits, expensive subscription",
        "recommended_app_title": "Sovereign Technical SEO & Architecture Auditor",
        "app_slug": "sovereign_technical_seo_auditor",
        "key_features_to_include": ["Meta tag validation", "Header security check", "OpenGraph preview", "Speed score"]
    }
    bp = diag.diagnose_target(sample_dossier)
    print("Architectural Blueprint:")
    print(json.dumps(bp, indent=2))
