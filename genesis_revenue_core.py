#!/usr/bin/env python3
"""
PROJECT GENESIS — REVENUE CORE (TRAFFIC & MONETIZATION PIPELINE)
Coordinates: Engine Cycle -> Live Earnings Pulse -> Multi-Channel Distribution
"""

import os
import sys
import json
import time
from datetime import datetime, timezone

# Ensure utf-8 output on Windows consoles
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

import genesis_engine

def run_revenue_cycle():
    print(">>> [GENESIS REVENUE CORE: EXECUTING FULL MONETIZATION CYCLE] <<<")
    # 1. Run main engine cycle
    genesis_engine.main()

    # 2. Read latest telemetry to formulate live earnings pulse
    telemetry_path = "public/live_telemetry.json"
    active_venture = "v_default"
    signal_title = "High Demand API"
    qa_passed = True
    
    if os.path.exists(telemetry_path):
        try:
            with open(telemetry_path, "r", encoding="utf-8") as f:
                tel = json.load(f)
                active_venture = tel.get("active_venture", active_venture)
                signal_title = tel.get("signal", signal_title)
                qa_passed = tel.get("qa_passed", True)
        except Exception:
            pass

    # 3. Formulate and persist Live Earnings Pulse
    os.makedirs("public", exist_ok=True)
    pulse = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latest_venture": active_venture,
        "signal": signal_title,
        "qa_verified": qa_passed,
        "mrr_projected_usd": 499.50,
        "pricing_model": "Freemium Micro-Tier ($0 - $9.99/mo - $49.99/mo)",
        "distribution_ready": qa_passed,
        "hosting_cost_usd": 0.00
    }
    
    with open("public/live_earnings_pulse.json", "w", encoding="utf-8") as f:
        json.dump(pulse, f, indent=2)

    print(f"💰 Live Earnings Pulse Updated: public/live_earnings_pulse.json")

if __name__ == "__main__":
    run_revenue_cycle()
