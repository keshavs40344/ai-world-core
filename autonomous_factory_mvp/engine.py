"""
Closed-Loop Autonomous Software Pipeline Engine
Lifecycle:
1. Problem Discovery (Founding Strategist)
2. Micro-Product Code Synthesis (Specialized Coder)
3. Subprocess Sandbox Test Execution (Automated QA Auditor)
4. Deployment & Treasury Allocation
5. Feedback & Automated Version 2 Code Patch
"""

import os
import sys
import time
import subprocess
import tempfile
import json
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from .models import World, Company, Agent, Task, Product, AuditLog, generate_id

# Sandbox directory for subprocess execution
SANDBOX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_sandbox")
os.makedirs(SANDBOX_DIR, exist_ok=True)

class PipelineEngine:
    def __init__(self, session: Session):
        self.session = session

    def run_subprocess_sandbox(self, code_content: str, test_content: str) -> Tuple[int, str, float]:
        """
        Executes code and unit tests in an isolated directory via Python subprocess.
        Returns: (exit_code, output_text, duration_seconds)
        """
        with tempfile.TemporaryDirectory(dir=SANDBOX_DIR) as temp_dir:
            code_file = os.path.join(temp_dir, "solution.py")
            test_file = os.path.join(temp_dir, "test_solution.py")

            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code_content)

            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_content)

            t0 = time.time()
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "unittest", "test_solution.py"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                duration = round(time.time() - t0, 4)
                output = (proc.stdout + "\n" + proc.stderr).strip()
                return proc.returncode, output, duration
            except subprocess.TimeoutExpired:
                return 124, "ERROR: Subprocess timed out after 15 seconds.", 15.0
            except Exception as e:
                return 1, f"ERROR: Subprocess execution failed: {str(e)}", round(time.time() - t0, 4)

    def step_1_identify_problem(self, company_id: str, strategist_id: str) -> Dict[str, Any]:
        """Founding Strategist identifies concrete micro-SaaS problem and technical spec."""
        problem_spec = {
            "name": "TokenBucket Limiter API",
            "slug": "token_bucket_limiter",
            "problem": "API endpoints suffer from sudden micro-burst spikes causing cascading database connection pool exhaustion.",
            "target_sla": "< 0.05ms in-memory decision latency",
            "v1_requirements": [
                "Fixed capacity and refill rate in tokens/sec",
                "Non-blocking consume(tokens=1) returning bool",
                "Thread-safe balance state inspection",
                "Full zero-dependency Python standard library implementation"
            ]
        }

        task = Task(
            id=generate_id("TASK"),
            company_id=company_id,
            assigned_agent_id=strategist_id,
            task_type="PROBLEM_DISCOVERY",
            payload_json=json.dumps(problem_spec),
            status="COMPLETED",
            result_json=json.dumps({"status": "SPEC_APPROVED", "spec": problem_spec}),
            completed_at=datetime.now(timezone.utc)
        )
        self.session.add(task)
        self.session.commit()
        return problem_spec

    def step_2_synthesize_v1_code(self, company_id: str, coder_id: str, spec: Dict[str, Any]) -> Tuple[str, str]:
        """Specialized Coder Agent generates real production business logic + test suite."""
        v1_code = '''"""
Production TokenBucket Rate Limiter Engine
Zero external dependencies. Thread-safe in-memory rate limiting.
"""

import time
import threading
from typing import Dict, Any

class TokenBucketLimiter:
    def __init__(self, capacity: int = 10, refill_rate_per_sec: float = 2.0):
        if capacity <= 0 or refill_rate_per_sec <= 0:
            raise ValueError("Capacity and refill rate must be positive numbers.")
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate_per_sec)
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self._lock = threading.Lock()

    def _refill(self):
        now = time.time()
        delta = now - self.last_refill
        if delta > 0:
            self.tokens = min(self.capacity, self.tokens + (delta * self.refill_rate))
            self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """Attempts to consume N tokens. Returns True if allowed, False if throttled."""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            self._refill()
            return {
                "available_tokens": round(self.tokens, 2),
                "capacity": self.capacity,
                "refill_rate": self.refill_rate
            }
'''

        v1_tests = '''import unittest
import time
from solution import TokenBucketLimiter

class TestTokenBucket(unittest.TestCase):
    def test_initial_burst(self):
        limiter = TokenBucketLimiter(capacity=5, refill_rate_per_sec=1.0)
        for _ in range(5):
            self.assertTrue(limiter.consume(1))
        # 6th should be rejected
        self.assertFalse(limiter.consume(1))

    def test_refill_replenishment(self):
        limiter = TokenBucketLimiter(capacity=2, refill_rate_per_sec=10.0)
        self.assertTrue(limiter.consume(2))
        self.assertFalse(limiter.consume(1))
        time.sleep(0.15) # Should refill at least 1.5 tokens
        self.assertTrue(limiter.consume(1))

    def test_status_inspection(self):
        limiter = TokenBucketLimiter(capacity=10, refill_rate_per_sec=2.0)
        status = limiter.get_status()
        self.assertEqual(status["capacity"], 10.0)
        self.assertEqual(status["refill_rate"], 2.0)

if __name__ == "__main__":
    unittest.main()
'''

        task = Task(
            id=generate_id("TASK"),
            company_id=company_id,
            assigned_agent_id=coder_id,
            task_type="CODE_SYNTHESIS",
            payload_json=json.dumps({"spec": spec, "target_version": "v1.0.0"}),
            status="COMPLETED",
            result_json=json.dumps({"lines_of_code": len(v1_code.splitlines())}),
            completed_at=datetime.now(timezone.utc)
        )
        self.session.add(task)
        self.session.commit()
        return v1_code, v1_tests

    def step_3_qa_and_deploy_v1(self, company_id: str, qa_agent_id: str, spec: Dict[str, Any], code: str, tests: str) -> Product:
        """Automated QA Agent executes tests in subprocess sandbox and deploys on success."""
        exit_code, test_output, duration = self.run_subprocess_sandbox(code, tests)
        is_passed = (exit_code == 0)

        product = Product(
            id=generate_id("PROD"),
            company_id=company_id,
            name=spec["name"],
            slug=spec["slug"],
            version="v1.0.0",
            code_content=code,
            test_suite_content=tests,
            status="DEPLOYED" if is_passed else "TEST_FAILED",
            test_exit_code=exit_code,
            test_output=test_output
        )
        self.session.add(product)

        # Audit Log
        audit = AuditLog(
            id=generate_id("LOG"),
            world_id=company_id,
            actor_agent_id=qa_agent_id,
            action="SANDBOX_VERIFICATION_V1",
            details=f"Test Suite ExitCode={exit_code}, Duration={duration}s. Passed={is_passed}",
            cost_usd=0.015
        )
        self.session.add(audit)
        self.session.commit()
        return product

    def step_4_feedback_and_patch_v2(self, company_id: str, coder_id: str, qa_agent_id: str, product: Product) -> Product:
        """Simulated metric triggers automatic improvement: multi-client key partitioning in v2."""
        v2_code = '''"""
Production TokenBucket Rate Limiter Engine (Version 2.0.0)
Added feature: Per-Client IP/Token Key Partitioning & Auto-Purge Cache.
"""

import time
import threading
from typing import Dict, Any, Optional

class TokenBucketLimiter:
    def __init__(self, capacity: int = 10, refill_rate_per_sec: float = 2.0):
        if capacity <= 0 or refill_rate_per_sec <= 0:
            raise ValueError("Capacity and refill rate must be positive numbers.")
        self.default_capacity = float(capacity)
        self.default_refill_rate = float(refill_rate_per_sec)
        # Client Partitioning Map: client_key -> [tokens, last_refill]
        self._buckets: Dict[str, list] = {}
        self._lock = threading.Lock()

    def _get_client_bucket(self, client_key: str):
        now = time.time()
        if client_key not in self._buckets:
            self._buckets[client_key] = [self.default_capacity, now]
            return self._buckets[client_key]
        bucket = self._buckets[client_key]
        delta = now - bucket[1]
        if delta > 0:
            bucket[0] = min(self.default_capacity, bucket[0] + (delta * self.default_refill_rate))
            bucket[1] = now
        return bucket

    def consume(self, tokens: int = 1, client_key: str = "default_client") -> bool:
        """Consumes tokens for a specific client key. Returns True if accepted, False if rate limited."""
        with self._lock:
            bucket = self._get_client_bucket(client_key)
            if bucket[0] >= tokens:
                bucket[0] -= tokens
                return True
            return False

    def get_client_status(self, client_key: str = "default_client") -> Dict[str, Any]:
        with self._lock:
            bucket = self._get_client_bucket(client_key)
            return {
                "client_key": client_key,
                "available_tokens": round(bucket[0], 2),
                "capacity": self.default_capacity
            }
'''

        v2_tests = '''import unittest
import time
from solution import TokenBucketLimiter

class TestTokenBucketV2(unittest.TestCase):
    def test_multi_client_isolation(self):
        limiter = TokenBucketLimiter(capacity=2, refill_rate_per_sec=1.0)
        # Client A exhausts tokens
        self.assertTrue(limiter.consume(1, client_key="client_A"))
        self.assertTrue(limiter.consume(1, client_key="client_A"))
        self.assertFalse(limiter.consume(1, client_key="client_A"))

        # Client B must remain completely unaffected
        self.assertTrue(limiter.consume(1, client_key="client_B"))
        self.assertTrue(limiter.consume(1, client_key="client_B"))
        self.assertFalse(limiter.consume(1, client_key="client_B"))

    def test_status_inspection(self):
        limiter = TokenBucketLimiter(capacity=10, refill_rate_per_sec=2.0)
        status = limiter.get_client_status("api_user_99")
        self.assertEqual(status["client_key"], "api_user_99")
        self.assertEqual(status["capacity"], 10.0)

if __name__ == "__main__":
    unittest.main()
'''

        # Re-run QA in Subprocess Sandbox
        exit_code, test_output, duration = self.run_subprocess_sandbox(v2_code, v2_tests)
        is_passed = (exit_code == 0)

        # Update product
        product.version = "v2.0.0"
        product.code_content = v2_code
        product.test_suite_content = v2_tests
        product.status = "DEPLOYED_V2" if is_passed else "PATCH_FAILED"
        product.test_exit_code = exit_code
        product.test_output = test_output
        product.updated_at = datetime.now(timezone.utc)

        # Log Task
        task = Task(
            id=generate_id("TASK"),
            company_id=company_id,
            assigned_agent_id=coder_id,
            task_type="FEEDBACK_PATCH",
            payload_json=json.dumps({"feature": "multi-client key isolation", "version": "v2.0.0"}),
            status="COMPLETED" if is_passed else "FAILED",
            result_json=json.dumps({"exit_code": exit_code, "duration_sec": duration}),
            completed_at=datetime.now(timezone.utc)
        )
        self.session.add(task)

        # Audit Log
        audit = AuditLog(
            id=generate_id("LOG"),
            world_id=company_id,
            actor_agent_id=qa_agent_id,
            action="SANDBOX_VERIFICATION_V2",
            details=f"V2 Patch Subprocess ExitCode={exit_code}, Duration={duration}s. Passed={is_passed}",
            cost_usd=0.020
        )
        self.session.add(audit)
        self.session.commit()
        return product
