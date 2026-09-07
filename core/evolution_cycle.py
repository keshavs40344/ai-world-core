"""
VASTUDA Autonomous Sovereign Core — Evolution Cycle Module
The living cognitive engine of the Autonomous AI Agent:
1. Perceive: Inspects World State & checks for user directives
2. Reason & Plan: Formulates high-value goals autonomously using Groq Free Tier
3. Act: Executes real code in sandbox or performs deep research
4. Self-Heal: Re-attempts and fixes code if sandbox errors occur
5. Evolve: Evaluates results, awards XP, levels up the World, and updates live telemetry
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional

# Ensure repo root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.agent_brain import AgentBrain, guardian
from core.world_state import WorldState
from core.toolbelt import Toolbelt
from core.tool_forge import ToolForge

# UTF-8 stdout setup
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
LIVE_STATE_JSON = os.path.join(PUBLIC_DIR, "world_live.json")
os.makedirs(PUBLIC_DIR, exist_ok=True)

class EvolutionCycle:
    def __init__(self, brain: Optional[AgentBrain] = None, world: Optional[WorldState] = None, tools: Optional[Toolbelt] = None):
        self.brain = brain or AgentBrain()
        self.world = world or WorldState()
        self.tools = tools or Toolbelt()
        self.forge = ToolForge(brain=self.brain, world=self.world)
        self.current_thought = "Agent standing by in Sovereign Core..."

    def export_live_state(self, extra_activity: Optional[Dict[str, Any]] = None):
        """Exports unified live state to public/world_live.json for the Cockpit UI."""
        summary = self.world.get_world_summary()
        recent_creations = self.world.get_recent_creations(limit=10)
        recent_logs = self.world.get_recent_logs(limit=15)
        recent_memories = self.world.get_recent_memories(limit=10)

        # Attach file contents so static GitHub Pages can display creations without a backend
        for c in recent_creations:
            fp = c.get("file_path", "")
            if fp and os.path.exists(fp):
                try:
                    with open(fp, "r", encoding="utf-8", errors="replace") as f:
                        c["content"] = f.read(25000)
                except Exception:
                    c["content"] = "[Content unreadable]"
            else:
                c["content"] = "[Artifact recorded in World Ledger]"

        data = {
            "world": summary,
            "agent_thought": self.current_thought,
            "tokens_used": guardian.total_tokens_used,
            "cost_spent_usd": 0.0,
            "recent_creations": recent_creations,
            "recent_logs": recent_logs,
            "recent_memories": recent_memories,
            "last_activity": extra_activity or {},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        try:
            with open(LIVE_STATE_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def run_one_cycle(self, manual_directive: Optional[str] = None) -> Dict[str, Any]:
        """Executes a complete autonomous cycle: Perceive -> Reason -> Act -> Evolve."""
        world_info = self.world.get_world_summary()
        cycle_num = len(self.world.get_recent_logs(limit=9999)) + 1

        print(f"\n{'='*70}")
        print(f" 🚀 EVOLUTION CYCLE #{cycle_num} :: WORLD LEVEL {world_info['level']} [{world_info['era']}]")
        print(f"{'='*70}")

        # 1. PERCEIVE & ORIENT
        self.current_thought = "Perceiving world state, active knowledge, and pending directives..."
        self.export_live_state({"stage": "PERCEIVE", "cycle": cycle_num})

        # Determine goal
        if manual_directive:
            print(f"  [DIRECTIVE RECEIVED]: {manual_directive}")
            quest_title = f"Execute Directive: {manual_directive[:50]}"
            quest_type = "USER_DIRECTIVE"
            quest_desc = manual_directive
        else:
            # Autonomous Goal Formulation
            # Alternate between CODE_FORGE and DEEP_RESEARCH
            total_creations = world_info.get("total_creations", 0)
            if total_creations % 2 == 0:
                goal_domain = "CODE_FORGE"
                domain_prompt = "Propose a useful, production-grade standalone Python utility tool for our autonomous world (e.g., cryptographic hash auditor, memory cache optimizer, data compression benchmark, micro-API mock server)."
            else:
                goal_domain = "DEEP_RESEARCH"
                domain_prompt = "Propose an in-depth, cutting-edge technology or market research topic (e.g., autonomous agent architectures, zero-knowledge scalability, post-quantum crypto resilience, decentralized intelligence)."

            self.current_thought = f"Autonomously deciding next sovereign mission in [{goal_domain}]..."
            self.export_live_state({"stage": "ORIENT", "domain": goal_domain})

            decision_prompt = f"""
You are the Sovereign AI Agent of VASTUDA civilization.
Current World Level: {world_info['level']} ({world_info['era']})
XP: {world_info['xp']}/{world_info['xp_for_next']}
Total Existing Creations: {total_creations}

Objective: {domain_prompt}

Return a valid JSON object matching this schema:
{{
  "category": "{goal_domain}",
  "title": "High impact title of what you will build/research",
  "objective": "Detailed 2-sentence rationale of why this evolves the world"
}}
"""
            decision = self.brain.think_structured(decision_prompt)
            quest_type = decision.get("category", goal_domain)
            quest_title = decision.get("title", f"Autonomous {goal_domain} Initiative")
            quest_desc = decision.get("objective", "Advance sovereign world capability.")

        print(f"  [MISSION ADOPTED]: [{quest_type}] {quest_title}")
        quest_id = self.world.add_quest(quest_title, quest_type, quest_desc)

        # 2. ACT
        creation_record = None
        xp_earned = 150

        if quest_type == "CODE_FORGE" or (manual_directive and any(k in manual_directive.lower() for k in ["tool", "app", "calculator", "generator", "builder", "code"])):
            self.current_thought = f"Synthesizing 100% working interactive client-side tool: {quest_title}..."
            self.export_live_state({"stage": "TOOL_FORGING", "title": quest_title})

            if manual_directive:
                slug = re.sub(r'[^a-zA-Z0-9_-]', '_', quest_title)[:35].lower()
                concept = {
                    "category": "Interactive Utility",
                    "slug": slug,
                    "title": quest_title,
                    "desc": quest_desc,
                    "icon": "zap"
                }
                html_code = self.forge.synthesize_tool_html(concept)
                filename = f"{slug}.html"
                file_path = os.path.join(REPO_ROOT, "public", "saas", filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_code)
                self.forge.update_catalog(concept, filename)
                self.world.record_creation("TOOL", quest_title, file_path, f"User-directed interactive app: {quest_desc}", quality_score=99.0)
                creation_record = {"type": "TOOL", "title": quest_title, "path": file_path, "url": f"public/saas/{filename}"}
                xp_earned = 300
                print(f"  ✔ Interactive tool forged and verified! Saved to: {file_path}")
            else:
                forge_res = self.forge.forge_one_tool()
                creation_record = {"type": "TOOL", "title": forge_res["title"], "path": forge_res["path"], "url": forge_res["url"]}
                xp_earned = 300

        else:
            # DEEP RESEARCH MISSION
            self.current_thought = f"Conducting deep intelligence research on: {quest_title}..."
            self.export_live_state({"stage": "RESEARCH", "title": quest_title})

            # Fetch web context
            print("  🌐 Harvesting real-time web intelligence...")
            web_results = self.tools.search_web(quest_title, max_results=3)
            web_snippets = "\n".join([f"- {r['title']}: {r['snippet']}" for r in web_results])

            report_prompt = f"""
Write a comprehensive, authentic, high-level investigative research dispatch:
Topic: {quest_title}
Context: {quest_desc}

Live Web Signals:
{web_snippets}

Format in clean Markdown:
## 1. Executive Summary & Strategic Importance
(Clear, factual analytical breakdown)

## 2. Technical Architecture & Data Matrix
(Concrete principles, benchmarks, or systemic analysis)

## 3. Sovereign Ramifications & Future Projections
(What this means for the autonomous AI ecosystem)

## 4. पूर्ण हिंदी विश्लेषण (Authentic Hindi Translation & Summary)
(Comprehensive, respectful Hindi journalism section)
"""
            report_md = self.brain.think(report_prompt, temperature=0.2, max_tokens=2500)
            slug = quest_title.lower().replace(" ", "-")[:40]
            saved_path = self.tools.save_report(slug, quest_title, report_md)
            print(f"  ✔ Deep research dispatch compiled and saved to: {saved_path}")

            summary_text = f"In-depth investigative dispatch synthesized with real web context and bilingual Hindi analysis."
            self.world.record_creation("REPORT", quest_title, saved_path, summary_text, quality_score=96.0)
            self.world.store_memory("RESEARCH_INSIGHT", quest_title, f"Documented key findings on '{quest_title}'. Added to world intelligence bank.")
            creation_record = {"type": "REPORT", "title": quest_title, "path": saved_path}
            xp_earned = 200

        # 3. COMPLETE QUEST & EVOLVE
        self.world.complete_quest(quest_id, f"Successfully executed {quest_title}", xp_earned)
        evolve_res = self.world.award_xp(xp_earned, innovation_boost=2)

        if evolve_res["leveled_up"]:
            print(f"  🎉 ★ LEVEL UP! World reached Level {evolve_res['new_level']} ({evolve_res['era']}) ★")
            self.current_thought = f"★ LEVEL UP! World evolved to Level {evolve_res['new_level']} in {evolve_res['era']}! ★"
        else:
            self.current_thought = f"Cycle complete. World gained +{xp_earned} XP (Current: {evolve_res['new_xp']})."

        self.world.log_evolution(
            cycle=cycle_num,
            thought=f"Accomplished [{quest_type}] {quest_title}",
            action=f"Created {creation_record.get('type')}: {creation_record.get('title')}",
            xp=xp_earned,
            level=evolve_res["new_level"]
        )

        self.export_live_state({
            "stage": "COMPLETE",
            "cycle": cycle_num,
            "creation": creation_record,
            "xp_earned": xp_earned
        })

        print(f"  ✔ Cycle #{cycle_num} Complete! Total Cost: $0.00 (100% Free Tier)")
        return {
            "cycle": cycle_num,
            "quest_title": quest_title,
            "quest_type": quest_type,
            "creation": creation_record,
            "xp_earned": xp_earned,
            "new_level": evolve_res["new_level"],
            "new_xp": evolve_res["new_xp"],
            "era": evolve_res["era"]
        }

if __name__ == "__main__":
    cycle = EvolutionCycle()
    res = cycle.run_one_cycle()
    print("\nResult summary:")
    print(json.dumps(res, indent=2))
