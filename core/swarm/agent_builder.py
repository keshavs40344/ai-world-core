"""
VASTUDA Swarm — Agent Builder (Master Application Engineer)
Receives the Architectural Blueprint from Agent Diagnostician.
Synthesizes a complete, 100% working, full-scale interactive web application (HTML5/Tailwind/ES6 JS).
Ensures zero paywalls, complete client-side execution, and superior UI/UX over expensive commercial SaaS.
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

class AgentBuilder:
    def __init__(self, brain: Optional[AgentBrain] = None, trainer: Optional[SwarmTrainingEngine] = None):
        self.brain = brain or AgentBrain()
        self.trainer = trainer or SwarmTrainingEngine()

    def build_application(self, dossier: Dict[str, Any], blueprint: Dict[str, Any]) -> str:
        """Synthesizes the complete, production-grade interactive single-file web application."""
        app_title = blueprint.get("app_title", "Sovereign Web Application")
        print(f"  [Builder] Engineering full-scale superior web application: '{app_title}'...")

        training_adapters = self.trainer.get_trained_prompt_adapters("Builder")

        prompt = f"""
You are Agent Builder, the Master Full-Stack Application Engineer of the VASTUDA Swarm.
Your mandate: Code a 100% COMPLETE, FULLY WORKING, production-grade interactive client-side web application.
This app must completely disrupt and outperform the commercial competitor: {dossier.get('target_name')} ({dossier.get('typical_price')}).

APP BLUEPRINT:
- Title: {app_title}
- Target Slug: {blueprint.get('app_slug')}
- Competitor: {dossier.get('target_name')}
- Architecture Layout: {blueprint.get('ui_layout')}
- Input Controls: {json.dumps(blueprint.get('input_controls', []))}
- Core Logic Specification: {blueprint.get('core_js_logic')}
- Visual Cards / Charts: {blueprint.get('visual_cards')}
- Export Capabilities: {blueprint.get('export_actions')}

{training_adapters}

MANDATORY CODING REQUIREMENTS:
1. Complete Single-File HTML5 with embedded <style> and <script>.
2. High-end modern UI: Tailwind CSS CDN + Inter / JetBrains Mono fonts + Lucide Icons CDN.
3. Realistic Interactive Controls: Custom sliders with live value counters, number inputs, dropdowns, and textareas.
4. REAL WORKING JAVASCRIPT:
   - Perform full mathematical formulas, parsers, or data visualizers.
   - Update outputs instantly on user input.
   - Include functioning Copy to Clipboard (navigator.clipboard) or Download file (blob).
   - Zero placeholder alerts (no 'alert(\"Coming soon\")' or fake stubs). Everything must be fully functional.
5. Zero paywalls, zero login, 100% client-side privacy.
6. CRITICAL LENGTH RULE: Keep CSS and JavaScript concise and modular so the ENTIRE application completes smoothly within token limits and ends with </script></body></html>.
7. Output ONLY valid HTML inside a ```html ``` block.
"""
        raw_html = self.brain.think(
            prompt,
            system_prompt="You are an elite principal software engineer who writes pristine, bug-free, fully-working single-page web applications.",
            temperature=0.15,
            max_tokens=4000
        )

        # Extract HTML
        if "```html" in raw_html:
            clean_html = raw_html.split("```html", 1)[1].split("```", 1)[0].strip()
        elif "```" in raw_html:
            clean_html = raw_html.split("```", 1)[1].split("```", 1)[0].strip()
        else:
            clean_html = raw_html.strip()

        # Continuation repair if cut off before closing tags
        if "</html>" not in clean_html:
            print("  [Builder] Incomplete markup detected (missing </html>). Running continuation repair...")
            repair_prompt = f"""The following HTML code for '{app_title}' was truncated near the end:
```html
{clean_html[-1200:]}
```
Provide the exact remaining HTML and JavaScript code needed to complete the application functionality and close all tags properly. End with </script></body></html>."""
            continuation = self.brain.think(
                repair_prompt,
                system_prompt="You complete truncated code accurately. Output ONLY the remaining code to finish the file.",
                temperature=0.1,
                max_tokens=2048
            )
            if "```html" in continuation:
                continuation = continuation.split("```html", 1)[1].split("```", 1)[0].strip()
            elif "```" in continuation:
                continuation = continuation.split("```", 1)[1].split("```", 1)[0].strip()
            clean_html = clean_html + "\n" + continuation

        if "<!DOCTYPE html>" not in clean_html and "<html" not in clean_html:
            clean_html = f"<!DOCTYPE html>\n<html lang=\"en\" class=\"dark\">\n<head><meta charset=\"UTF-8\"><title>{app_title}</title></head>\n<body>\n{clean_html}\n</body>\n</html>"

        return clean_html

if __name__ == "__main__":
    builder = AgentBuilder()
    print("Agent Builder ready.")
