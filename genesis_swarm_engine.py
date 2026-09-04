import sys

# Windows UTF-8 console output
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

from genesis.swarm.orchestrator import SwarmOrchestrator

def main():
    orchestrator = SwarmOrchestrator()
    orchestrator.run_cycle()

if __name__ == "__main__":
    main()
