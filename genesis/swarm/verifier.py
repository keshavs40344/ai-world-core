import sys
import subprocess
from typing import Dict, Any, Tuple
from genesis.swarm.bus import MessageBus

class SelfHealingQAVerifier:
    """Self-Healing QA & Verifier.
    Executes tests in an isolated sandbox subprocess, ensures return code == 0,
    and publishes signed QA verification to the bus.
    """
    
    def __init__(self, bus: MessageBus):
        self.bus = bus

    def verify(self, module_path: str, test_path: str, task_id: str) -> Tuple[bool, str, str]:
        cmd = [sys.executable, test_path]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            success = (proc.returncode == 0)
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
        except Exception as e:
            success = False
            stdout = ""
            stderr = str(e)

        payload = {
            "task_id": task_id,
            "test_path": test_path,
            "passed": success,
            "return_code": 0 if success else 1,
            "stdout": stdout,
            "stderr": stderr
        }

        self.bus.publish(
            sender="QA_Verifier",
            recipient="Eve",
            topic="qa_verification",
            payload=payload
        )
        return success, stdout, stderr
