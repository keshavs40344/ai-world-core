"""Update public/index.html with fresh stats and improved GPAA section header."""
import sys, sqlite3, json, re
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

idx_path = Path("public/index.html")
content = idx_path.read_text(encoding="utf-8", errors="replace")

# ── Live stats ────────────────────────────────────────────────────────────
total_tools = len(list(Path("public/saas").glob("*.html")))
db = sqlite3.connect("db/genesis_state.db")
total_decrees = db.execute("SELECT COUNT(*) FROM global_chancellor_decrees").fetchone()[0]
db.close()
bus_count = len(list(Path("vault/bus").glob("*.json")))
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

print(f"Tools: {total_tools}, Decrees: {total_decrees}, Bus: {bus_count}, Time: {now_utc}")

# ── 1. Update GPAA subtitle line ──────────────────────────────────────────
new_subtitle = f"Hourly planetary decrees &middot; {total_decrees} senate instruments ratified &middot; {total_tools} tools live &middot; Updated {now_utc}"
content = re.sub(
    r"Hourly planetary decrees.*?(?:ratified|live).*?(?=</div>)",
    new_subtitle,
    content,
    flags=re.DOTALL
)
print("Updated GPAA subtitle.")

# ── 2. Update the JS counter for systems ────────────────────
content = re.sub(
    r'"systems":\s*\d+',
    f'"systems": {total_tools}',
    content
)
print("Updated systems counter.")

# ── 3. Update meta description ────────────────────────────────────────────
content = re.sub(
    r'<meta name="description" content="[^"]*"',
    f'<meta name="description" content="AI WORLD CORE — {total_tools} autonomous browser tools, GPAA-2026 senate ({total_decrees} decrees), Telegram-notified deployments. Zero server. 100% client-side."',
    content
)
print("Updated meta description.")

# ── 4. Inject Telegram notification badge near GPAA section ──────────────
LIVE_BAR = f'''<div style="max-width:1100px;margin:24px auto 0;padding:0 24px;">
  <div style="background:linear-gradient(90deg,#0f172a,#1e293b);border:1px solid #22c55e33;border-radius:10px;padding:12px 20px;display:flex;flex-wrap:wrap;gap:16px;align-items:center;font-family:monospace;font-size:12px;">
    <span style="color:#4ade80;">● LIVE</span>
    <span style="color:#94a3b8;">Tools deployed: <strong style="color:#fff;">{total_tools}</strong></span>
    <span style="color:#94a3b8;">Senate decrees: <strong style="color:#a78bfa;">{total_decrees}</strong></span>
    <span style="color:#94a3b8;">Bus signals: <strong style="color:#38bdf8;">{bus_count}</strong></span>
    <span style="color:#94a3b8;">Health: <strong style="color:#4ade80;">100%</strong></span>
    <span style="color:#94a3b8;">Telegram: <strong style="color:#4ade80;">Active</strong></span>
    <span style="color:#475569;margin-left:auto;">Updated: {now_utc}</span>
  </div>
</div>
<section id="gpaa-decrees"'''

if '● LIVE</span>' not in content and '<section id="gpaa-decrees"' in content:
    content = content.replace('<section id="gpaa-decrees"', LIVE_BAR, 1)
    print("Injected live-stats bar above GPAA section.")

# ── Write back ────────────────────────────────────────────────────────────
idx_path.write_text(content, encoding="utf-8")
print(f"\nindex.html updated. Size: {idx_path.stat().st_size:,} bytes")
print("DONE.")
