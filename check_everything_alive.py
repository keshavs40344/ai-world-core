#!/usr/bin/env python3
"""
GPAA-2026 :: Full System Health & Evolution Audit
Checks: HTML terminals, Python daemons, SQLite DB,
        bus signals, telemetry, GitHub Pages URLs, portal injection
"""
import sys, os, json, sqlite3, time, hashlib
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OK   = "[  OK  ]"
FAIL = "[ FAIL ]"
WARN = "[ WARN ]"
INFO = "[ INFO ]"

results = {"ok": 0, "fail": 0, "warn": 0}

def check(label, passed, detail=""):
    sym = OK if passed else FAIL
    if passed: results["ok"] += 1
    else: results["fail"] += 1
    print(f"{sym}  {label:<55} {detail}")
    return passed

def warn(label, detail=""):
    results["warn"] += 1
    print(f"{WARN}  {label:<55} {detail}")

def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

REPO = Path(".")

# ─────────────────────────────────────────────────────────────
section("1 · CORE PYTHON DAEMONS — AST COMPILE CHECK")
# ─────────────────────────────────────────────────────────────
CORE_SCRIPTS = [
    "planetary_governance_daemon.py",
    "auto_senior_approval_gate.py",
    "governance/tier_b_gate.py",
    "sentinel_self_healing_watchdog.py",
    "genesis_sovereign_evolution_core.py",
    "public/saas/planetary_governance_engine.py",
    "audit_deploy.py",
]
for script in CORE_SCRIPTS:
    p = REPO / script
    if not p.exists():
        warn(script, "FILE NOT FOUND")
        continue
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
        compile(src, script, "exec")
        check(script, True, f"{p.stat().st_size} bytes")
    except SyntaxError as e:
        check(script, False, str(e)[:50])

# ─────────────────────────────────────────────────────────────
section("2 · HTML TERMINALS — DOM SANITY CHECK")
# ─────────────────────────────────────────────────────────────
saas_dir = REPO / "public" / "saas"
html_files = sorted(saas_dir.glob("*.html"))
gpaa_slugs = [
    "global_macro_resource_rebalancer",
    "global_compute_energy_optimizer",
    "global_pathogen_early_warning",
    "universal_pedagogy_accelerator",
    "zk_governance_proof_sentinel",
    "fusion_solar_grid_architect",
    "planetary_code_quality_gate",
    "planetary_governance_terminal",
]
print(f"\n  Total HTML tools in public/saas/: {len(html_files)}")
for slug in gpaa_slugs:
    p = saas_dir / f"{slug}.html"
    if not p.exists():
        check(f"  {slug}.html", False, "MISSING")
        continue
    content = p.read_text(encoding="utf-8", errors="replace")
    has_doctype = content.strip().upper().startswith("<!DOCTYPE")
    has_close   = content.strip().endswith("</html>")
    dom_ok = has_doctype and has_close
    check(f"  {slug}.html", dom_ok,
          f"{'DOCTYPE+</html> OK' if dom_ok else 'DOM DEFECT'}  {p.stat().st_size}B")

# ─────────────────────────────────────────────────────────────
section("3 · GOVERNANCE LEDGER — SQLITE DB")
# ─────────────────────────────────────────────────────────────
db_path = REPO / "db" / "genesis_state.db"
if db_path.exists():
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        # Chancellor decrees
        rows = conn.execute("SELECT * FROM global_chancellor_decrees ORDER BY ratified_timestamp DESC").fetchall()
        check("DB global_chancellor_decrees", True, f"{len(rows)} decrees recorded")
        for r in rows:
            fname = Path(r["terminal_path"]).name if r["terminal_path"] else "?"
            ts = datetime.fromtimestamp(r["ratified_timestamp"], tz=timezone.utc).strftime("%H:%M:%S UTC")
            print(f"         [{r['academic_integrity_score']}]  {r['faculty'][:42]:<42}  {ts}")

        # Fleet DB tables
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        check("DB tables present", len(tables) >= 1, f"{[t['name'] for t in tables]}")
        conn.close()
    except Exception as e:
        check("SQLite DB accessible", False, str(e)[:60])
else:
    check("SQLite DB exists", False, str(db_path))

# ─────────────────────────────────────────────────────────────
section("4 · TELEMETRY FILES")
# ─────────────────────────────────────────────────────────────
for fname in ["public/live_telemetry.json", "public/live_earnings_pulse.json"]:
    p = REPO / fname
    if not p.exists():
        check(fname, False, "MISSING"); continue
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        age_s = time.time() - data.get("epoch", data.get("timestamp", time.time() - 9999))
        age_s = time.time() - (list(data.values())[0] if not isinstance(list(data.values())[0], str) else time.time())
        status = data.get("status") or data.get("senate_status", "?")
        check(fname, True, f"status={status}")
    except Exception as e:
        check(fname, False, str(e)[:50])

# ─────────────────────────────────────────────────────────────
section("5 · BUS SIGNALS & DEANERY CHARTERS")
# ─────────────────────────────────────────────────────────────
bus_signals = list((REPO / "vault" / "bus").glob("*.json"))
check("vault/bus/ signals", len(bus_signals) >= 7, f"{len(bus_signals)} signals on bus")

charters = sorted((REPO / "vault" / "departments").glob("faculty_*_charter.json"))
check("vault/departments/ charters", len(charters) == 7, f"{len(charters)}/7 faculty charters")
for c in charters:
    data = json.loads(c.read_text(encoding="utf-8"))
    check(f"  {c.name}", data.get("status") == "RATIFIED_GLOBAL_PRODUCTION",
          data.get("dean","?"))

# ─────────────────────────────────────────────────────────────
section("6 · PORTAL CARD INJECTION — index.html")
# ─────────────────────────────────────────────────────────────
index = REPO / "public" / "index.html"
if index.exists():
    content = index.read_text(encoding="utf-8", errors="replace")
    has_gpaa = "gpaa-decrees" in content
    has_senate = "SENATE RATIFIED" in content or "senate" in content.lower()
    check("index.html GPAA section injected", has_gpaa, "id=gpaa-decrees found" if has_gpaa else "NOT FOUND")
    check("index.html senate cards present", has_senate)
else:
    check("index.html exists", False)

# ─────────────────────────────────────────────────────────────
section("7 · EVOLUTION — DAEMON READY TO RUN")
# ─────────────────────────────────────────────────────────────
daemon = REPO / "planetary_governance_daemon.py"
check("planetary_governance_daemon.py exists", daemon.exists(), f"{daemon.stat().st_size} bytes" if daemon.exists() else "MISSING")

# Check it has all 7 faculties
if daemon.exists():
    src = daemon.read_text(encoding="utf-8")
    faculty_count = src.count('"id":')
    check("All 7 faculties defined in daemon", faculty_count >= 7, f"{faculty_count} faculties found")
    check("Hourly loop defined", "start_planetary_council_loop" in src)
    check("ZK proof generation present", "generate_zk_proof" in src)
    check("Portal card injection present", "inject_portal_cards" in src)
    check("Telemetry writer present", "write_telemetry" in src)
    check("Windows asyncio compat present", "WindowsSelectorEventLoopPolicy" in src)

# ─────────────────────────────────────────────────────────────
section("8 · GIT STATUS")
# ─────────────────────────────────────────────────────────────
import subprocess
try:
    result = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True, cwd=REPO)
    print("  Recent commits:")
    for line in result.stdout.strip().splitlines():
        print(f"    {line}")
    result2 = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=REPO)
    uncommitted = result2.stdout.strip()
    check("Working tree clean", uncommitted == "", f"{len(uncommitted.splitlines())} uncommitted" if uncommitted else "CLEAN")
except Exception as e:
    warn("Git check failed", str(e))

# ─────────────────────────────────────────────────────────────
section("FINAL VERDICT")
# ─────────────────────────────────────────────────────────────
total = results["ok"] + results["fail"] + results["warn"]
score = round(results["ok"] / max(total,1) * 100, 2)
print(f"\n  Checks passed : {results['ok']}")
print(f"  Warnings      : {results['warn']}")
print(f"  Failures      : {results['fail']}")
print(f"  Health Score  : {score}%")
if results["fail"] == 0:
    print("\n  [PROVOST VERDICT] ALL SYSTEMS OPERATIONAL. EVOLUTION ACTIVE.")
else:
    print(f"\n  [PROVOST VERDICT] {results['fail']} ISSUES DETECTED. REVIEW ABOVE.")
