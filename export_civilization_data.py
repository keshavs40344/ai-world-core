#!/usr/bin/env python3
"""
CIVILIZATION CONTROL CENTER DATA SERIALIZER
Generates public/civilization_state.json directly from db/civilization_core.db
for the real-time interactive civilization dashboard.
"""

import os
import sys
import json
import sqlite3
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CIV_DB = os.path.join(ROOT_DIR, "db", "civilization_core.db")
OUTPUT_JSON = os.path.join(ROOT_DIR, "public", "civilization_state.json")

def export_civilization_state():
    conn = sqlite3.connect(CIV_DB, timeout=20.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    world = dict(cur.execute("SELECT * FROM civ_worlds LIMIT 1").fetchone() or {})

    continents = [dict(r) for r in cur.execute("SELECT * FROM civ_continents ORDER BY id").fetchall()]
    companies = [dict(r) for r in cur.execute("SELECT * FROM civ_companies ORDER BY id").fetchall()]
    agents = [dict(r) for r in cur.execute("SELECT * FROM civ_agents ORDER BY id").fetchall()]
    products = [dict(r) for r in cur.execute("SELECT * FROM civ_products ORDER BY created_at DESC").fetchall()]
    events = [dict(r) for r in cur.execute("SELECT * FROM civ_world_events ORDER BY id DESC LIMIT 25").fetchall()]
    transactions = [dict(r) for r in cur.execute("SELECT * FROM civ_transactions ORDER BY id DESC LIMIT 25").fetchall()]
    test_runs = [dict(r) for r in cur.execute("SELECT * FROM civ_test_runs ORDER BY id DESC LIMIT 25").fetchall()]

    conn.close()

    total_val = sum(c.get("valuation", 0.0) for c in companies)
    total_rev = sum(c.get("monthly_revenue", 0.0) for c in companies)
    total_treasury = sum(c.get("treasury_balance", 0.0) for c in companies)

    payload = {
        "world": world,
        "metrics": {
            "total_continents": len(continents),
            "total_companies": len(companies),
            "total_agents": len(agents),
            "total_products": len(products),
            "total_valuation_usd": total_val,
            "total_monthly_revenue_usd": total_rev,
            "total_treasury_usd": total_treasury,
            "system_status": world.get("status", "ACTIVE"),
            "last_tick": events[0]["tick"] if events else 1,
            "last_updated_epoch": time.time()
        },
        "continents": continents,
        "companies": companies,
        "agents": agents,
        "products": products,
        "events": events,
        "transactions": transactions,
        "test_runs": test_runs
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"✔ Exported civilization state: {OUTPUT_JSON} ({len(products)} products, {len(events)} events)")

if __name__ == "__main__":
    export_civilization_state()
