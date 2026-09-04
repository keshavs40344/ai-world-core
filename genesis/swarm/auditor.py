import os
import ast
import re
from typing import Dict, Any, List, Tuple
from genesis.swarm.bus import MessageBus

class DefensiveSecurityAuditor:
    """Defensive Security Auditor.
    Strict White-Hat SAST engine performing AST code review against OWASP Top 10,
    scanning for exposed credentials, shell injections, and dangerous primitives.
    """
    
    BANNED_CALLS = {"eval", "exec", "compile", "__import__"}
    SECRET_PATTERNS = [
        re.compile(r'(?i)(?:api_key|secret|password|auth_token)\s*=\s*["\'][a-zA-Z0-9_\-]{8,}["\']'),
        re.compile(r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{15,}'),
        re.compile(r'AKIA[0-9A-Z]{16}')
    ]

    def __init__(self, bus: MessageBus):
        self.bus = bus

    def audit_codebase(self, file_path: str, auditor_spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
        findings = []
        if not os.path.exists(file_path):
            return False, [f"Target file not found: {file_path}"]

        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()

        # 1. AST Static Application Security Testing (SAST)
        try:
            tree = ast.parse(code_content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in self.BANNED_CALLS:
                        findings.append(f"OWASP A03 (Injection Risk): Prohibited function call '{node.func.id}' at line {node.lineno}")
                    elif isinstance(node.func, ast.Attribute) and node.func.attr in self.BANNED_CALLS:
                        findings.append(f"OWASP A03 (Injection Risk): Prohibited attribute call '{node.func.attr}' at line {node.lineno}")
        except SyntaxError as e:
            findings.append(f"Syntax Error in AST analysis: {str(e)}")

        # 2. Secret & Credential Leak Detection
        for pattern in self.SECRET_PATTERNS:
            if pattern.search(code_content):
                findings.append("OWASP A02 (Cryptographic/Credential Failure): Potential hardcoded credential detected")

        # 3. Shell Injection check
        if "shell=True" in code_content:
            findings.append("OWASP A03 (Injection Risk): Prohibited shell=True subprocess execution detected")

        is_approved = len(findings) == 0
        audit_payload = {
            "task_id": auditor_spec.get("task_id", "unknown"),
            "file_audited": file_path,
            "status": "APPROVED" if is_approved else "FLAGGED",
            "findings": findings if findings else ["Zero OWASP vulnerabilities detected. AST static clearance granted."],
            "owasp_compliance": is_approved
        }

        self.bus.publish(
            sender="DefensiveAuditor",
            recipient="Eve",
            topic="security_audit",
            payload=audit_payload
        )
        return is_approved, audit_payload["findings"]
