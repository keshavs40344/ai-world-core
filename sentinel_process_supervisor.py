import os
import sys
import time
import socket
import subprocess
import urllib.request
import sqlite3

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = "http://127.0.0.1:8000/api/v1/system/telemetry"
SAAS_DIR = os.path.join(ROOT_DIR, "public", "saas")

def is_server_alive() -> bool:
    """Checks if FastAPI backend is responding."""
    try:
        req = urllib.request.Request(SERVER_URL, headers={"User-Agent": "SentinelWatchdog/3.0"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.getcode() == 200
    except Exception:
        return False

def run_supervisor_loop(single_run=False):
    print("==================================================================")
    print("👁️ [SENTINEL AUTONOMOUS SUPERVISOR]: Active 24/7 Watchdog Online")
    print("   Monitoring Server Heartbeat, Tool Integrity, and Fleet Health")
    print("==================================================================")

    server_process = None

    while True:
        # 1. Server Health Check
        alive = is_server_alive()
        if not alive:
            print(f"[{time.strftime('%H:%M:%S')}] ⚠️ [ALERT]: Server on port 8000 unresponsive or offline.")
            if server_process is None or server_process.poll() is not None:
                print("   └── 🔧 [AUTO-REPAIR]: Spawning sovereign_production_server.py...")
                server_process = subprocess.Popen([sys.executable, "sovereign_production_server.py"])
                time.sleep(3)
        else:
            # 2. Real Socket Outbound Check
            t0 = time.perf_counter()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                s.connect(("1.1.1.1", 53))
                s.close()
                latency = round((time.perf_counter() - t0) * 1000, 2)
                fleet_len = len(os.listdir(SAAS_DIR)) if os.path.exists(SAAS_DIR) else 0
                print(f"[{time.strftime('%H:%M:%S')}] ✓ [HEARTBEAT OK] Server Active | DNS Ping: {latency}ms | Fleet Size: {fleet_len}")
            except Exception:
                print(f"[{time.strftime('%H:%M:%S')}] ⚠️ [NETWORK DEGRADED] Internet outbound packet loss detected.")

        if single_run:
            break
        time.sleep(2.0)

if __name__ == "__main__":
    is_once = "--once" in sys.argv
    run_supervisor_loop(single_run=is_once)
