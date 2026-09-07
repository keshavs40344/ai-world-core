"""
VASTUDA Autonomous Sovereign Core — Cockpit Web Server
Lightweight, zero-dependency REST & UI server using Python standard library.
Serves the live World Cockpit dashboard and receives autonomous directives.
"""

import os
import sys
import json
import sqlite3
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure repo root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.world_state import WorldState
from core.evolution_cycle import EvolutionCycle
from core.agent_brain import guardian

PORT = 8088
PUBLIC_DIR = os.path.join(REPO_ROOT, "public")
COCKPIT_HTML = os.path.join(PUBLIC_DIR, "world_cockpit.html")

cycle_engine = EvolutionCycle()
cycle_lock = threading.Lock()

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
                "recent_memories": memories
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
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
            with cycle_lock:
                result = cycle_engine.run_one_cycle()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        if path == "/api/directive":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body) if body else {}
            directive = data.get("directive", "")

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
