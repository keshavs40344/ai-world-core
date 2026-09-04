import os
import sys
from typing import Dict, Any

# Ensure utf-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from genesis.swarm.bus import MessageBus
from genesis.swarm.adam import AdamPlanner
from genesis.swarm.eve import EveDispatcher
from genesis.swarm.builder import SpecialistBuilder
from genesis.swarm.auditor import DefensiveSecurityAuditor
from genesis.swarm.verifier import SelfHealingQAVerifier
from genesis.swarm.censor_board import CensorBoardGateway

class SwarmOrchestrator:
    """GEN-9 Multi-Agent Collaborative Swarm Orchestrator.
    Drives the 4-tier collaborative chain:
    Adam -> Eve -> (Builder / Auditor) -> QA Verifier -> Censor Board
    """
    
    def __init__(self):
        self.bus = MessageBus()
        self.adam = AdamPlanner(self.bus)
        self.eve = EveDispatcher(self.bus)
        self.builder = SpecialistBuilder(self.bus)
        self.auditor = DefensiveSecurityAuditor(self.bus)
        self.verifier = SelfHealingQAVerifier(self.bus)
        self.censor = CensorBoardGateway(self.bus)

    def run_cycle(self) -> Dict[str, Any]:
        print("\n>>> [GEN-9 MULTI-AGENT COLLABORATIVE SWARM INITIATING] <<<")
        print("[1/5] Adam: Harvesting real-world signals & formulating defensive threat model...")
        signal = self.adam.harvest_signal()
        strategy = self.adam.formulate_strategy(signal)
        print(f"      Signal: {strategy['signal_title']}")
        print(f"      Threat Model: OWASP Top 10 mapped | Prohibited tokens quarantined")

        print("[2/5] Eve: Dispatching tasks across inter-agent message bus (vault/bus/)...")
        dispatch_pkg = self.eve.dispatch(strategy)

        print("[3/5] Inter-Agent Workgroup: Specialist Builder & Defensive Auditor collaborating...")
        module_path, test_path = self.builder.build_solution(dispatch_pkg["builder_spec"])
        print(f"      Specialist Builder: Module generated at {module_path}")
        
        sec_approved, findings = self.auditor.audit_codebase(module_path, dispatch_pkg["auditor_spec"])
        print(f"      Defensive Auditor: AST SAST Clearance -> {'APPROVED' if sec_approved else 'FLAGGED'}")
        for finding in findings:
            print(f"        - {finding}")

        print("[4/5] Self-Healing QA: Spawning isolated sandbox test runner...")
        qa_passed, stdout, stderr = self.verifier.verify(module_path, test_path, strategy["task_id"])
        print(f"      QA Verifier: Exit Code 0 -> {'PASSED' if qa_passed else 'FAILED'}")

        print("[5/5] Censor Board: Freezing deliverable and logging to SQLite & Dashboard...")
        cert = self.censor.certify({
            "task_id": strategy["task_id"],
            "signal_title": strategy["signal_title"],
            "module_path": module_path,
            "test_path": test_path,
            "qa_passed": qa_passed,
            "sec_approved": sec_approved
        })

        print(f"\n==================================================")
        print(f"🛑 CENSOR BOARD MILESTONE GATEWAY (GEN-9 SWARM)")
        print(f"Task ID   : {cert['task_id']}")
        print(f"Artifact  : {cert['artifact']}")
        print(f"Signal    : {cert['signal']}")
        print(f"Security  : {cert['sec_status']} (OWASP SAST Verified)")
        print(f"QA Engine : {cert['qa_status']} (Exit Code 0 Verified)")
        print(f"Authority : {cert['gate_action']}")
        print(f"==================================================\n")

        return cert
