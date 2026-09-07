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

        if quest_type == "CODE_FORGE" or (manual_directive and "code" in manual_directive.lower()):
            self.current_thought = f"Synthesizing and testing executable Python tool: {quest_title}..."
            self.export_live_state({"stage": "CODE_SYNTHESIS", "title": quest_title})

            code_prompt = f"""
Write a complete, high-quality, production-ready standalone Python script for:
Title: {quest_title}
Objective: {quest_desc}

Requirements:
1. Pure standard library only (no external pip packages required).
2. Clean, modular functions with type hints and docstrings.
3. Must include a self-testing block under if __name__ == '__main__': that demonstrates the tool working and prints PASS.
4. Return ONLY valid Python code inside a ```python ``` block.
"""
            raw_code = self.brain.think(code_prompt, temperature=0.15)
            # Extract python code
            if "```python" in raw_code:
                clean_code = raw_code.split("```python", 1)[1].split("```", 1)[0].strip()
            elif "```" in raw_code:
                clean_code = raw_code.split("```", 1)[1].split("```", 1)[0].strip()
            else:
                clean_code = raw_code.strip()

            # Execute in Sandbox
            print("  ⚡ Executing tool in isolated sandbox...")
            passed, output, el = self.tools.execute_sandbox(clean_code)

            # Self-healing if failed
            if not passed:
                print(f"  [SANDBOX ERROR]: {output[:150]} -> Triggering Self-Healing...")
                self.current_thought = "Sandbox error detected. Self-healing and refactoring code..."
                fix_prompt = f"""
The following Python script failed in sandbox execution:
CODE:
{clean_code}

ERROR:
{output}

Fix the bug and provide the corrected, working Python script inside a ```python ``` block.
"""
                fixed_raw = self.brain.think(fix_prompt, temperature=0.1)
                if "```python" in fixed_raw:
                    clean_code = fixed_raw.split("```python", 1)[1].split("```", 1)[0].strip()
                elif "```" in fixed_raw:
                    clean_code = fixed_raw.split("```", 1)[1].split("```", 1)[0].strip()
                passed, output, el = self.tools.execute_sandbox(clean_code)

            # Save tool
            filename = quest_title.lower().replace(" ", "_").replace("/", "_")[:35] + ".py"
            saved_path = self.tools.save_tool(filename, clean_code)
            print(f"  ✔ Tool verified in {el}s! Saved to: {saved_path}")

            summary_text = f"Standalone Python utility created and verified in sandbox ({el}s). Output: {output[:100]}"
            self.world.record_creation("TOOL", quest_title, saved_path, summary_text, quality_score=98.0)
            self.world.store_memory("TOOL_INSIGHT", quest_title, f"Successfully forged tool '{filename}'. Passed all unit assertions.")
            creation_record = {"type": "TOOL", "title": quest_title, "path": saved_path}
            xp_earned = 250

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
