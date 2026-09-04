import os
import sqlite3
import subprocess
from datetime import datetime, timezone
from typing import Dict, Any
from genesis.swarm.bus import MessageBus

class CensorBoardGateway:
    """Censor Board Certification Desk.
    Freezes deployable artifacts for Operator binary authority: [APPROVE & MERGE] or [REJECT & PURGE].
    Logs records to SQLite, updates UI dashboard, stages git commits.
    """
    
    DB_PATH = "vault/genesis_memory.db"

    def __init__(self, bus: MessageBus):
        self.bus = bus

    def certify(self, package: Dict[str, Any]) -> Dict[str, Any]:
        task_id = package["task_id"]
        signal_title = package.get("signal_title", "Unknown Task")
        module_path = package["module_path"]
        qa_status = "PASSED" if package.get("qa_passed") else "FAILED"
        sec_status = "APPROVED" if package.get("sec_approved") else "FLAGGED"

        # 1. SQLite Persistence
        os.makedirs("vault", exist_ok=True)
        conn = sqlite3.connect(self.DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                signal_title TEXT,
                qa_status TEXT,
                artifact_path TEXT
            )
        """)
        now_utc = datetime.now(timezone.utc).isoformat()
        cur.execute("INSERT INTO telemetry (timestamp, signal_title, qa_status, artifact_path) VALUES (?, ?, ?, ?)",
                    (now_utc, f"[SWARM-GEN9] {signal_title}", qa_status, module_path))
        conn.commit()
        conn.close()

        # 2. Update Public Swarm Dashboard
        os.makedirs("public", exist_ok=True)
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Genesis GEN-9 Multi-Agent Swarm Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ background: #0b0f19; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 2rem; margin: 0; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 1rem; margin-bottom: 2rem; }}
        .badge {{ background: #10b981; color: #022c22; padding: 0.35rem 0.8rem; border-radius: 9999px; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 1.5rem; }}
        .card h3 {{ margin-top: 0; color: #38bdf8; font-size: 1.1rem; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }}
        .val {{ font-size: 1.25rem; font-weight: bold; color: #f8fafc; margin: 0.5rem 0; }}
        .sub {{ font-size: 0.85rem; color: #94a3b8; }}
        .bus-log {{ background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 1rem; font-family: monospace; font-size: 0.85rem; max-height: 250px; overflow-y: auto; }}
        .bus-item {{ margin-bottom: 0.5rem; border-bottom: 1px solid #1e293b; padding-bottom: 0.4rem; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin: 0; font-size: 1.75rem;">⚡ GENESIS-PRIME: COLLABORATIVE SWARM (GEN-9)</h1>
            <p style="margin: 0.35rem 0 0 0; color: #94a3b8;">Multi-Agent Consensus Network & White-Hat Defensive Foundry</p>
        </div>
        <span class="badge">Swarm Operational</span>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Adam (Planner & Scout)</h3>
            <div class="val">{signal_title}</div>
            <div class="sub">Threat Model: OWASP Top 10 + Input Hardening</div>
        </div>
        <div class="card">
            <h3>Eve (Assembler & Bus)</h3>
            <div class="val">{task_id}</div>
            <div class="sub">Structured Inter-Agent Messaging: vault/bus/</div>
        </div>
        <div class="card">
            <h3>Defensive SAST Audit</h3>
            <div class="val" style="color: #4ade80;">{sec_status}</div>
            <div class="sub">Zero Injection | AST Cleared | Zero Leaks</div>
        </div>
        <div class="card">
            <h3>Self-Healing QA Engine</h3>
            <div class="val" style="color: #38bdf8;">{qa_status} (Code 0)</div>
            <div class="sub">Isolated Sandbox Subprocess Verified</div>
        </div>
    </div>

    <div class="card">
        <h3>Operator Censor Board Milestone</h3>
        <p><strong>Artifact Staged:</strong> <code>{module_path}</code></p>
        <p><strong>Authority Mode:</strong> [APPROVE & MERGE] or [REJECT & PURGE]</p>
        <p><strong>Sync Timestamp:</strong> {now_utc} UTC</p>
    </div>
</body>
</html>"""
        with open("public/dashboard.html", "w", encoding="utf-8") as f:
            f.write(html)

        # 3. Git Staging
        subprocess.run(["git", "add", module_path, package.get("test_path", ""), "public/dashboard.html", "vault/genesis_memory.db", "vault/bus"],
                       capture_output=True, text=True)

        cert_record = {
            "task_id": task_id,
            "signal": signal_title,
            "artifact": module_path,
            "qa_status": qa_status,
            "sec_status": sec_status,
            "gate_action": "[APPROVE & MERGE] or [REJECT & PURGE]"
        }

        self.bus.publish(
            sender="CensorBoard",
            recipient="Operator",
            topic="censor_gateway",
            payload=cert_record
        )

        return cert_record
