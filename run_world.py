"""
VASTUDA Sovereign Core — World Launcher (run_world.py)
One-click entrypoint to start the Autonomous AI Agent & Living World.

Usage:
  python run_world.py               # Starts Live Cockpit UI (http://localhost:8088)
  python run_world.py --cycle       # Runs one autonomous cycle immediately from CLI
  python run_world.py --autopilot   # Runs continuous autonomous loop every 10 minutes
"""

import os
import sys
import time
import argparse
import webbrowser
import threading

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.evolution_cycle import EvolutionCycle
from core.web_server import run_server, PORT

def autopilot_worker(interval_seconds: int = 600):
    """Background worker that continuously evolves the world on autopilot."""
    engine = EvolutionCycle()
    print(f"[*] Autopilot daemon active. Running evolution cycle every {interval_seconds} seconds.")
    while True:
        try:
            print("\n[*] Autopilot heartbeat: initiating scheduled evolution cycle...")
            engine.run_one_cycle()
        except Exception as e:
            print(f"[!] Autopilot cycle error: {e}")
        time.sleep(interval_seconds)

def main():
    parser = argparse.ArgumentParser(description="VASTUDA Autonomous Sovereign Core Launcher")
    parser.add_argument("--cycle", action="store_true", help="Run a single autonomous cycle from CLI and exit")
    parser.add_argument("--autopilot", action="store_true", help="Run continuous background evolution loop")
    parser.add_argument("--port", type=int, default=PORT, help="Port for the Live Cockpit UI (default 8088)")
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-launch browser")
    args = parser.parse_args()

    if args.cycle:
        engine = EvolutionCycle()
        engine.run_one_cycle()
        return

    if args.autopilot:
        # Start background autopilot loop
        t = threading.Thread(target=autopilot_worker, daemon=True)
        t.start()

    # Open browser after a brief delay
    if not args.no_browser:
        def open_browser():
            time.sleep(1.0)
            webbrowser.open(f"http://localhost:{args.port}")
        threading.Thread(target=open_browser, daemon=True).start()

    # Start the Cockpit Web Server
    run_server(port=args.port)

if __name__ == "__main__":
    main()
