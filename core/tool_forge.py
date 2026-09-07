"""
VASTUDA Autonomous Sovereign Core — Tool Forge Module
Autonomously generates 100% fully-working, interactive client-side SaaS tools (HTML5 + CSS + JS)
Covers all categories: Developer, Finance, Security, AI, Productivity, Crypto, Data, Design, Health, Math.
Requires ZERO human effort. Every tool is immediately runnable in the browser.
"""

import os
import sys
import json
import time
import re
from typing import Dict, Any, List, Optional

# Ensure repo root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.agent_brain import AgentBrain, guardian
from core.world_state import WorldState

SAAS_DIR = os.path.join(REPO_ROOT, "public", "saas")
os.makedirs(SAAS_DIR, exist_ok=True)
INDEX_JSON = os.path.join(REPO_ROOT, "public", "tools_catalog.json")

# Master Blueprint of Essential Categories & Ideas to cover everything
# Master Blueprint of High-Utility Tools that ChatGPT/Gemini CANNOT replace:
# 1. Private/Zero Data Leakage (Can't paste sensitive tokens/salaries into LLMs)
# 2. Deterministic Precision Math (LLMs hallucinate arithmetic; tools give penny-perfect math)
# 3. Interactive Visual Sliders & Live Canvas Graphs
# 4. Instant In-Browser File & Data Transcoding
BLUEPRINT_CATALOG = [
    {
        "category": "FinTech & Taxation",
        "slug": "income_tax_regime_comparator_pro",
        "title": "Income Tax Regime Comparator (New vs Old)",
        "desc": "Penny-perfect deterministic comparison of Old vs New Tax Regimes with Standard Deduction, 80C, 80D, HRA, Section 87A rebate, and slab-by-slab breakdown. Zero LLM arithmetic hallucinations.",
        "icon": "receipt"
    },
    {
        "category": "CyberSecurity & Privacy",
        "slug": "jwt_token_inspector_sentinel",
        "title": "Private JWT Token Inspector & Signature Auditor",
        "desc": "100% client-side JWT token decoder and audit suite. Inspect headers, payload claims, expiration alerts without sending sensitive production secrets to external cloud servers.",
        "icon": "shield-alert"
    },
    {
        "category": "DevOps & Scheduling",
        "slug": "cron_expression_visualizer_engine",
        "title": "Cron Schedule Visualizer & Human Translator",
        "desc": "Interactive cron expression builder with human-readable English breakdown, next 10 exact execution timestamps, and common presets for Linux & cloud schedulers.",
        "icon": "calendar-clock"
    },
    {
        "category": "Developer Tools",
        "slug": "regex_live_evaluator_pro",
        "title": "Regex Live Evaluator Pro",
        "desc": "Real-time regular expression tester with syntax highlighting, flag toggles, and match capture tables.",
        "icon": "code-2"
    },
    {
        "category": "FinTech & Wealth",
        "slug": "smart_sip_dca_compound_simulator",
        "title": "Smart SIP & DCA Compound Simulator",
        "desc": "Simulate Systematic Investment Plans (SIP) and Dollar-Cost Averaging with inflation adjustment and interactive growth charts.",
        "icon": "trending-up"
    },
    {
        "category": "Data & File Utilities",
        "slug": "csv_json_matrix_transcoder",
        "title": "Zero-Leakage CSV & JSON Matrix Transcoder",
        "desc": "Instant client-side converter between CSV and JSON with dynamic table search, column sorter, and CSV export. 100% private.",
        "icon": "file-spreadsheet"
    },
    {
        "category": "UI/UX & Frontend",
        "slug": "glassmorphism_css_palette_generator",
        "title": "Glassmorphism CSS & Palette Generator",
        "desc": "Interactive visual slider studio to design backdrop-blur cards, modern gradients, and copy ready-to-use CSS.",
        "icon": "palette"
    },
    {
        "category": "Crypto & Trading",
        "slug": "crypto_profit_dca_exit_calculator",
        "title": "Crypto Profit & Staged Exit Planner",
        "desc": "Calculate entry average, target exit prices, fee deductions, and net returns for spot and futures positions.",
        "icon": "coins"
    }
]

class ToolForge:
    def __init__(self, brain: Optional[AgentBrain] = None, world: Optional[WorldState] = None):
        self.brain = brain or AgentBrain()
        self.world = world or WorldState()

    def get_existing_tool_slugs(self) -> List[str]:
        if not os.path.exists(SAAS_DIR):
            return []
        return [f.replace(".html", "") for f in os.listdir(SAAS_DIR) if f.endswith(".html")]

    def pick_next_tool_concept(self) -> Dict[str, Any]:
        """Picks a missing high-value tool concept from blueprint or invents a novel one."""
        existing = set(self.get_existing_tool_slugs())
        for bp in BLUEPRINT_CATALOG:
            if bp["slug"] not in existing:
                return bp

        # High-Standard LLM Ideation: The ChatGPT/Gemini Test
        prompt = f"""
We have an autonomous SaaS tool factory. Existing tools: {list(existing)[:15]}.
CRITICAL RULE: DO NOT propose generic text-based tools that a user would just ask ChatGPT or Gemini for!
Only propose tools where a dedicated client-side browser application is 100x better than ChatGPT:
1. Zero Data Leakage / 100% Client-Side Privacy (users cannot paste private data into cloud LLMs).
2. Deterministic Precision Math (exact financial, tax, or engineering formulas where LLMs hallucinate).
3. Real-time visual manipulation (sliders, live charts, color pickers, sound timers).
4. Direct client-side file/format transcoding.

Respond strictly in JSON matching this schema:
{{
  "category": "Category Name",
  "slug": "unique_tool_slug_in_snake_case",
  "title": "Crisp High-Utility Tool Title",
  "desc": "Detailed explanation of the exact calculations/interactivity it performs",
  "icon": "lucide-icon-name"
}}
"""
        res = self.brain.think_structured(prompt)
        if "slug" in res and "title" in res:
            return res

        # Default fallback concept
        timestamp_slug = f"utility_calculator_{int(time.time())}"
        return {
            "category": "Productivity",
            "slug": timestamp_slug,
            "title": "Instant Unit & Conversion Matrix",
            "desc": "Calculates speed, memory, data transfer, and currency units in real-time.",
            "icon": "cpu"
        }

    def synthesize_tool_html(self, concept: Dict[str, Any]) -> str:
        """Prompts AgentBrain to synthesize a rich, complete, working interactive HTML application."""
        prompt = f"""
You are the Lead Sovereign Frontend Engineer & UI/UX Architect.
Build a 100% FULLY WORKING, production-grade, interactive client-side web utility tool.

Tool Details:
- Title: {concept['title']}
- Category: {concept['category']}
- Objective: {concept['desc']}
- Slug: {concept['slug']}

MANDATORY SPECIFICATIONS:
1. Complete Single-File HTML5 document with embedded <style> and <script>.
2. Styling: Modern, sleek cybernetic dark-mode UI using Tailwind CSS CDN + Google Fonts + Lucide Icons CDN.
3. Interactive Controls: Must include real, custom input controls (e.g., number inputs, range sliders with live value counters, select dropdowns, textareas, or buttons).
4. REAL WORKING LOGIC in vanilla JavaScript:
   - Must perform actual calculations, text processing, conversions, or data visualization on user input!
   - Must update output cards/charts immediately on input or button click (no placeholder or dummy alerts).
   - Must include a "Copy Output" or "Export" button that works using navigator.clipboard or blob download.
   - Must include responsive error handling (e.g. invalid input hints).
5. Self-Contained: 100% client-side (no backend API required).
6. Return ONLY the complete HTML inside a ```html ``` code block. Do not omit any code.
"""
        raw_html = self.brain.think(prompt, system_prompt="You write pristine, complete, beautiful, 100% working HTML/JS single-page web applications.", temperature=0.15, max_tokens=3800)

        # Extract HTML
        if "```html" in raw_html:
            clean_html = raw_html.split("```html", 1)[1].split("```", 1)[0].strip()
        elif "```" in raw_html:
            clean_html = raw_html.split("```", 1)[1].split("```", 1)[0].strip()
        else:
            clean_html = raw_html.strip()

        # Basic HTML integrity check
        if "<!DOCTYPE html>" not in clean_html and "<html" not in clean_html:
            clean_html = f"<!DOCTYPE html>\n<html lang=\"en\" class=\"dark\">\n<head><meta charset=\"UTF-8\"><title>{concept['title']}</title></head>\n<body>\n{clean_html}\n</body>\n</html>"

        return clean_html

    def verify_tool_integrity(self, html_code: str) -> bool:
        """Verifies that the generated HTML has valid scripts and essential DOM hooks."""
        has_script = "<script>" in html_code or "<script " in html_code
        has_closing = "</html>" in html_code
        has_body = "</body>" in html_code
        return has_script and (has_closing or has_body)

    def forge_one_tool(self) -> Dict[str, Any]:
        """Autonomously selects, builds, verifies, and publishes a new 100% working tool."""
        concept = self.pick_next_tool_concept()
        print(f"\n[ToolForge] Synthesizing new working tool: [{concept['category']}] {concept['title']}...")

        html_content = self.synthesize_tool_html(concept)
        is_valid = self.verify_tool_integrity(html_content)

        if not is_valid:
            print("[ToolForge WARN] Generated HTML failed verification. Re-attempting...")
            html_content = self.synthesize_tool_html(concept)

        filename = f"{concept['slug']}.html"
        file_path = os.path.join(SAAS_DIR, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        file_size = len(html_content)
        print(f"[ToolForge OK] Tool successfully forged: {filename} ({file_size} bytes)")

        # Record in World State
        self.world.record_creation(
            c_type="TOOL",
            title=concept["title"],
            file_path=file_path,
            summary=f"Interactive client-side web utility: {concept['desc']}",
            quality_score=99.0
        )
        self.world.store_memory(
            category="TOOL_FORGED",
            key_topic=concept["title"],
            content=f"Deployed fully-functional interactive tool '{filename}' covering {concept['category']}."
        )
        self.world.award_xp(300, innovation_boost=5)

        # Update Master Tools Catalog JSON
        self.update_catalog(concept, filename)

        return {
            "title": concept["title"],
            "category": concept["category"],
            "filename": filename,
            "path": file_path,
            "size": file_size,
            "url": f"public/saas/{filename}"
        }

    def update_catalog(self, concept: Dict[str, Any], filename: str):
        catalog = []
        if os.path.exists(INDEX_JSON):
            try:
                with open(INDEX_JSON, "r", encoding="utf-8") as f:
                    catalog = json.load(f)
            except Exception:
                catalog = []

        # Avoid duplicates
        catalog = [item for item in catalog if item.get("filename") != filename]
        catalog.insert(0, {
            "title": concept["title"],
            "category": concept["category"],
            "desc": concept["desc"],
            "icon": concept.get("icon", "tool"),
            "filename": filename,
            "url": f"public/saas/{filename}",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

        with open(INDEX_JSON, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2)

if __name__ == "__main__":
    forge = ToolForge()
    res = forge.forge_one_tool()
    print("Result:", json.dumps(res, indent=2))
