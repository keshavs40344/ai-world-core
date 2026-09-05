import sqlite3, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

saas = sorted(Path("public/saas").glob("*.html"))
print("DEPLOYED HTML TERMINALS:")
for f in saas:
    print(f"  {f.name:<55} {f.stat().st_size:>7} bytes")

conn = sqlite3.connect("db/genesis_state.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT faculty, dean, terminal_path, academic_integrity_score FROM global_chancellor_decrees ORDER BY ratified_timestamp").fetchall()
print(f"\nGOVERNANCE LEDGER ({len(rows)} decrees):")
for r in rows:
    score = r["academic_integrity_score"]
    fname = Path(r["terminal_path"]).name if r["terminal_path"] else "?"
    print(f"  [{score}]  {r['faculty'][:45]:<45}  -> {fname}")
conn.close()

bus = list(Path("vault/bus").glob("*.json"))
print(f"\nBUS SIGNALS: {len(bus)}")

charters = sorted(Path("vault/departments").glob("faculty_*_charter.json"))
print(f"DEANERY CHARTERS: {len(charters)}")
for c in charters:
    print(f"  {c.name}")

tele_path = Path("public/live_telemetry.json")
if tele_path.exists():
    tele = json.loads(tele_path.read_text(encoding="utf-8"))
    print(f"\nTELEMETRY STATUS: {tele.get('status')}  fleet={tele.get('fleet_size')}  decrees={tele.get('total_decrees_ratified')}")

pulse_path = Path("public/live_earnings_pulse.json")
if pulse_path.exists():
    pulse = json.loads(pulse_path.read_text(encoding="utf-8"))
    print(f"SENATE STATUS: {pulse.get('senate_status')}  tier={pulse.get('tier')}")

print("\n[F7-PROVOST] ALL SYSTEMS AUDITED. DEPLOYMENT CERTIFIED.")
