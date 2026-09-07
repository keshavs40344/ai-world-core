"""
VASTUDA Sovereign Core — Multi-Agent Swarm Orchestrator (swarm_orchestrator.py)
Coordinates the 4-Agent Autonomous Swarm:
[1. Scout] ➔ [2. Diagnostician] ➔ [3. Builder] ➔ [4. QA Trainer]
Disrupts expensive $20-$100/mo SaaS products with superior, 100% free client-side applications.
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.agent_brain import AgentBrain, guardian
from core.world_state import WorldState
from core.free_mesh import FreeResourceMesh
from core.training_engine import SwarmTrainingEngine
from core.swarm.agent_scout import AgentScout
from core.swarm.agent_diagnostician import AgentDiagnostician
from core.swarm.agent_builder import AgentBuilder
from core.swarm.agent_trainer import AgentTrainer

PUBLIC_DIR = os.path.join(REPO_ROOT, "public")
LIVE_STATE_JSON = os.path.join(PUBLIC_DIR, "world_live.json")

class SwarmOrchestrator:
    def __init__(self):
        self.brain = AgentBrain()
        self.world = WorldState()
        self.mesh = FreeResourceMesh()
        self.training_engine = SwarmTrainingEngine()

        # The 4 Autonomous Specialist Agents
        self.scout = AgentScout(brain=self.brain, mesh=self.mesh, trainer=self.training_engine)
        self.diagnostician = AgentDiagnostician(brain=self.brain, trainer=self.training_engine)
        self.builder = AgentBuilder(brain=self.brain, trainer=self.training_engine)
        self.trainer = AgentTrainer(trainer=self.training_engine, world=self.world)

        self.current_thought = "Swarm standing by on Sovereign Grid..."
        self.active_phase = "IDLE"

    def execute_disruption_mission(self, manual_target: Optional[str] = None) -> Dict[str, Any]:
        """Executes a full 4-agent swarm cycle to research, reverse-engineer, build, and train."""
        world_info = self.world.get_world_summary()
        existing_creations = self.world.get_recent_creations(limit=50)
        existing_slugs = [c.get("title", "").lower().replace(" ", "_") for c in existing_creations]

        cycle_num = len(self.world.get_recent_logs(limit=9999)) + 1
        print(f"\n{'='*75}")
        print(f" 🐝 MULTI-AGENT SWARM ACTIVE :: CYCLE #{cycle_num} :: WORLD LEVEL {world_info['level']}")
        print(f"{'='*75}")

        # PHASE 1: SCOUT
        self.active_phase = "SCOUTING"
        self.current_thought = "🕵️‍♂️ Agent Scout scanning web for expensive SaaS targets charging $20-$120/mo..."
        self.export_swarm_state({"phase": "SCOUTING", "cycle": cycle_num})

        if manual_target:
            intel = self.mesh.harvest_target_intelligence(manual_target)
            dossier = {
                "target_name": manual_target,
                "niche": "High-Value Web Application",
                "typical_price": "$49/mo",
                "user_pain_points": "Expensive subscription, paywalls, data leakage",
                "disruptive_opportunity": f"Deliver a 100% free client-side {manual_target} studio",
                "recommended_app_title": f"Sovereign {manual_target} Studio",
                "app_slug": manual_target.lower().replace(" ", "_")[:30],
                "key_features_to_include": ["Full Workflow", "Live Interactive Controls", "Zero Paywall", "Instant Export"],
                "web_intel": intel
            }
        else:
            dossier = self.scout.scout_next_target(existing_slugs)

        print(f"  [+] Target Identified: {dossier.get('target_name')} ({dossier.get('typical_price')})")
        print(f"      Opportunity: {dossier.get('disruptive_opportunity')}")

        # PHASE 2: DIAGNOSTICIAN
        self.active_phase = "DIAGNOSING"
        self.current_thought = f"🔬 Agent Diagnostician reverse-engineering architecture of {dossier.get('target_name')}..."
        self.export_swarm_state({"phase": "DIAGNOSING", "target": dossier.get('target_name')})

        blueprint = self.diagnostician.diagnose_target(dossier)
        print(f"  [+] Architecture Blueprint Designed: '{blueprint.get('app_title')}'")

        # PHASE 3: BUILDER
        self.active_phase = "BUILDING"
        self.current_thought = f"🏗️ Agent Builder synthesizing full-scale superior web application '{blueprint.get('app_title')}'..."
        self.export_swarm_state({"phase": "BUILDING", "app": blueprint.get('app_title')})

        html_code = self.builder.build_application(dossier, blueprint)

        # PHASE 4: QA TRAINER
        self.active_phase = "TRAINING_AND_DEPLOYING"
        self.current_thought = f"🧪 Agent Trainer running QA audits and updating swarm self-training weights..."
        self.export_swarm_state({"phase": "TRAINING", "app": blueprint.get('app_title')})

        deploy_result = self.trainer.audit_and_deploy(dossier, blueprint, html_code)

        # Log Evolution
        evolve_res = self.world.get_world_summary()
        self.world.log_evolution(
            cycle=cycle_num,
            thought=f"Disrupted {dossier.get('target_name')} with free client-side '{deploy_result['title']}'",
            action=f"Deployed full-scale web application: {deploy_result['filename']}",
            xp=400,
            level=evolve_res["level"]
        )

        training_summary = self.training_engine.get_training_summary()

        self.current_thought = f"★ Mission Complete! Disrupted {dossier.get('target_name')}. Swarm IQ: {training_summary['vitals']['swarm_iq']} (Accuracy: {training_summary['vitals']['accuracy_score']}%)"
        self.active_phase = "IDLE"

        self.export_swarm_state({
            "phase": "COMPLETE",
            "deployed": deploy_result,
            "swarm_vitals": training_summary["vitals"]
        })

        print(f"\n  🎉 ★ DISRUPTION SUCCESSFUL! ★")
        print(f"  App Live at: public/saas/{deploy_result['filename']}")
        print(f"  Swarm IQ: {training_summary['vitals']['swarm_iq']} | Accuracy: {training_summary['vitals']['accuracy_score']}%")
        print(f"  Total Cost: $0.00 (100% Free Lifetime)")

        return {
            "dossier": dossier,
            "blueprint": blueprint,
            "deploy_result": deploy_result,
            "swarm_vitals": training_summary["vitals"]
        }

    def export_swarm_state(self, extra: Optional[Dict[str, Any]] = None):
        """Exports unified state including multi-agent status and training metrics."""
        summary = self.world.get_world_summary()
        recent_creations = self.world.get_recent_creations(limit=10)
        recent_logs = self.world.get_recent_logs(limit=12)
        training_summary = self.training_engine.get_training_summary()

        # Attach content for static viewing
        for c in recent_creations:
            fp = c.get("file_path", "")
            if fp and os.path.exists(fp):
                try:
                    with open(fp, "r", encoding="utf-8", errors="replace") as f:
                        c["content"] = f.read(25000)
                except Exception:
                    c["content"] = "[Content unreadable]"

        data = {
            "world": summary,
            "agent_thought": self.current_thought,
            "active_phase": self.active_phase,
            "tokens_used": guardian.total_tokens_used,
            "cost_spent_usd": 0.0,
            "swarm_vitals": training_summary["vitals"],
            "recent_lessons": training_summary["recent_lessons"],
            "recent_creations": recent_creations,
            "recent_logs": recent_logs,
            "extra": extra or {},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        try:
            with open(LIVE_STATE_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

if __name__ == "__main__":
    swarm = SwarmOrchestrator()
    res = swarm.execute_disruption_mission()
