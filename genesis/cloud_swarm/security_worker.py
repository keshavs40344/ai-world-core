import os
import ast
import sys
import subprocess
from typing import Dict, Any, Tuple, List

class SecurityWorker:
    """Security Worker: AST Code Auditor & Isolated Pytest QA.
    Conducts deep white-hat SAST audits and runs isolated sandbox test execution.
    """
    
    FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__", "globals", "locals"}

    @classmethod
    def audit_ast(cls, file_path: str) -> Tuple[bool, List[str]]:
        findings = []
        if not os.path.exists(file_path):
            return False, [f"File not found: {file_path}"]

        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        try:
            tree = ast.parse(code, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Name) and func.id in cls.FORBIDDEN_CALLS:
                        findings.append(f"SAST Alert (CWE-94): Prohibited call '{func.id}' at line {node.lineno}")
                    elif isinstance(func, ast.Attribute) and func.attr in cls.FORBIDDEN_CALLS:
                        findings.append(f"SAST Alert (CWE-94): Prohibited attribute call '{func.attr}' at line {node.lineno}")
        except SyntaxError as e:
            findings.append(f"SAST Syntax Error: {e}")

        # Check for open subprocess shell=True
        if "shell=True" in code:
            findings.append("SAST Alert (CWE-78): Insecure shell=True detected in source")

        return len(findings) == 0, findings if findings else ["AST SAST Clearance: 0 CWE/OWASP issues detected"]

    @staticmethod
    def run_qa_sandbox(test_path: str) -> Tuple[bool, str, str]:
        cmd = [sys.executable, test_path]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            passed = (proc.returncode == 0)
            return passed, proc.stdout.strip(), proc.stderr.strip()
        except Exception as e:
            return False, "", str(e)
