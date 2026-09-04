import sys

# Windows & Linux console UTF-8 support
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

from genesis.cloud_swarm.eve_prime import EvePrimeMotherEngine

def main():
    engine = EvePrimeMotherEngine()
    engine.run_cloud_cycle()

if __name__ == "__main__":
    main()
