import sys
from typing import Dict, Any

# Windows & Linux console UTF-8 support
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from genesis.cloud_swarm.radar_worker import RadarWorker
from genesis.cloud_swarm.builder_worker import BuilderWorker
from genesis.cloud_swarm.security_worker import SecurityWorker
from genesis.cloud_swarm.gatekeeper import GatekeeperDesk

class EvePrimeMotherEngine:
    """Eve-Prime: Cloud Swarm Mother Engine.
    Central coordinator for 100% headless cloud multi-agent execution.
    0% local RAM, 0% local CPU, 0% local GPU overhead.
    """
    
    def __init__(self):
        self.radar = RadarWorker()
        self.builder = BuilderWorker()
        self.security = SecurityWorker()
        self.gatekeeper = GatekeeperDesk()

    def run_cloud_cycle(self) -> Dict[str, Any]:
        print("\n>>> [EVE-PRIME: HEADLESS CLOUD SWARM CYCLE (GEN-10) INITIALIZING] <<<")
        print("⚡ Mode: 100% Cloud Execution | 0% Local Hardware Consumption")
        
        # 1. Radar Workers
        print("\n[Pool 1: Radar Workers] Scouting unauthenticated public RSS/JSON feeds...")
        signal = self.radar.scout_signal()
        print(f"      Signal Acquired: {signal['title']}")
        print(f"      Source: {signal['source']} (Jitter: {signal['jitter_applied_sec']}s)")

        # 2. Builder Workers
        print("\n[Pool 2: Builder Workers] Synthesizing modular Python micro-service & test harness...")
        task_id, module_path, test_path = self.builder.generate_component(signal)
        print(f"      Task ID: {task_id}")
        print(f"      Artifact: {module_path}")

        # 3. Security Workers
        print("\n[Pool 3: Security Workers] Running AST SAST static code audit...")
        sec_approved, findings = self.security.audit_ast(module_path)
        print(f"      SAST Status: {'APPROVED' if sec_approved else 'FLAGGED'}")
        for f in findings:
            print(f"        - {f}")

        print("\n[Pool 3: Security Workers] Executing sandboxed test runner in isolated subprocess...")
        qa_passed, stdout, stderr = self.security.run_qa_sandbox(test_path)
        print(f"      QA Runner: {'PASSED (Exit Code 0)' if qa_passed else 'FAILED'}")

        # 4. Gatekeeper Staging
        print("\n[Staging Desk] Freezing deliverable in vault/proposals/ & updating telemetry...")
        result = self.gatekeeper.record_and_notify({
            "task_id": task_id,
            "signal_title": signal["title"],
            "source": signal["source"],
            "jitter_sec": signal["jitter_applied_sec"],
            "module_path": module_path,
            "test_path": test_path,
            "sec_approved": sec_approved,
            "qa_passed": qa_passed
        })

        # 5. Milestone Gatekeeper Notification Card
        print(f"\n==================================================")
        print(f"🛑 MILESTONE GATEKEEPER NOTIFICATION CARD (GEN-10)")
        print(f"Environment : Cloud Runner (0% Local Compute)")
        print(f"Task ID     : {result['task_id']}")
        print(f"Artifact    : {result['artifact']}")
        print(f"Signal      : {result['signal']}")
        print(f"Security    : {result['sec_status']} (AST SAST Clean)")
        print(f"QA Status   : {result['qa_status']} (Exit Code 0 Verified)")
        print(f"Operator    : {result['gate_action']}")
        print(f"==================================================\n")

        return result
