"""
VASTUDA Autonomous Sovereign Core — Cockpit Web Server
Lightweight, zero-dependency REST & UI server using Python standard library.
Serves the live World Cockpit dashboard and receives autonomous directives.
"""

import os
import sys
import json
import time
import sqlite3
import threading
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure repo root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.world_state import WorldState
from core.evolution_cycle import EvolutionCycle
from core.agent_brain import guardian
from core.training_engine import SwarmTrainingEngine
from core.swarm_orchestrator import SwarmOrchestrator

PORT = 8088
PUBLIC_DIR = os.path.join(REPO_ROOT, "public")
COCKPIT_HTML = os.path.join(PUBLIC_DIR, "world_cockpit.html")

cycle_engine = EvolutionCycle()
swarm_engine = SwarmOrchestrator()
cycle_lock = threading.Lock()

terminal_logs = [
    {"time": time.strftime("%H:%M:%S"), "source": "SWARM", "text": "VASTUDA Swarm Grid Online. All 4 Agents active."}
]

def log_terminal(source: str, text: str):
    t_str = time.strftime("%H:%M:%S")
    terminal_logs.append({"time": t_str, "source": source, "text": text})
    if len(terminal_logs) > 60:
        terminal_logs.pop(0)

class CockpitHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ["/", "/cockpit", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(COCKPIT_HTML, "rb") as f:
                self.wfile.write(f.read())
            return

        if path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            world_summary = cycle_engine.world.get_world_summary()
            creations = cycle_engine.world.get_recent_creations(limit=8)
            logs = cycle_engine.world.get_recent_logs(limit=12)
            memories = cycle_engine.world.get_recent_memories(limit=8)

            payload = {
                "world": world_summary,
                "agent_thought": cycle_engine.current_thought,
                "tokens_used": guardian.total_tokens_used,
                "cost_spent_usd": 0.0,
                "recent_creations": creations,
                "recent_logs": logs,
                "recent_memories": memories,
                "swarm_training": SwarmTrainingEngine().get_training_summary()
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        if path.startswith("/api/quote"):
            qs = parse_qs(parsed.query)
            ticker = qs.get("ticker", ["AAPL"])[0].upper().strip()
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    raw = json.loads(resp.read().decode())
                    meta = raw["chart"]["result"][0]["meta"]
                    price = meta.get("regularMarketPrice", 0)
                    curr = meta.get("currency", "USD")
                    prev = meta.get("previousClose", price)
                    high52 = meta.get("fiftyTwoWeekHigh", 0)
                    low52 = meta.get("fiftyTwoWeekLow", 0)
                    change_pct = round(((price - prev) / prev) * 100, 2) if prev else 0.0

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "ticker": ticker,
                        "price": price,
                        "currency": curr,
                        "previous_close": prev,
                        "change_pct": change_pct,
                        "high_52w": high52,
                        "low_52w": low52
                    }).encode("utf-8"))
                    log_terminal("LIVE_FEED", f"Fetched live quote for {ticker}: {price} {curr}")
                    return
            except Exception as e:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "ticker": ticker}).encode("utf-8"))
                return

        if path == "/api/terminal-logs":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"logs": terminal_logs}).encode("utf-8"))
            return

        if path.startswith("/api/creations/"):
            creation_id_str = path.split("/api/creations/")[1]
            try:
                c_id = int(creation_id_str)
                with cycle_engine.world._get_conn() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM creations WHERE id = ?", (c_id,))
                    row = cur.fetchone()
                if row:
                    file_path = row["file_path"]
                    content = ""
                    if os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                            content = f.read()
                    else:
                        content = f"[File not found at: {file_path}]"
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "id": c_id,
                        "title": row["title"],
                        "type": row["type"],
                        "content": content
                    }).encode("utf-8"))
                    return
            except Exception as e:
                pass
            self.send_response(404)
            self.end_headers()
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/run-cycle":
            log_terminal("CYCLE", "Autonomous cycle requested.")
            with cycle_lock:
                result = cycle_engine.run_one_cycle()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path == "/api/disrupt":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body) if body else {}
            target = data.get("target", "").strip()

            log_terminal("DISRUPT", f"Deploying Multi-Agent Swarm against: {target or 'Autonomous Top Target'}")

            with cycle_lock:
                result = swarm_engine.execute_disruption_mission(manual_target=target if target else None)

            deployed = result.get("deploy_result", {})
            log_terminal("DISRUPT_SUCCESS", f"Disrupted target! Live at: public/saas/{deployed.get('filename', '')}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path == "/api/directive":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body) if body else {}
            directive = data.get("directive", "")

            log_terminal("DIRECTIVE", f"User directive received: {directive}")

            with cycle_lock:
                result = cycle_engine.run_one_cycle(manual_directive=directive)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server(port: int = PORT):
    server = ThreadingHTTPServer(("0.0.0.0", port), CockpitHandler)
    print(f"\n=======================================================")
    print(f"  VASTUDA SOVEREIGN COCKPIT ONLINE")
    print(f"  Access Dashboard at: http://localhost:{port}")
    print(f"=======================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    run_server()
