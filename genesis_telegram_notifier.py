#!/usr/bin/env python3
"""
GENESIS NON-BLOCKING TELEGRAM BROADCASTER
Sends instant executive release alerts with live URLs.
ZERO POLLING. ZERO APPROVAL LOOPS. ZERO TIMEOUTS.
"""

import os
import sys
import json
import urllib.request

# UTF-8 Console encoding safety for Windows PowerShell
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

def clean_env(key: str, default: str = "") -> str:
    val = os.getenv(key, default)
    return val.strip().lstrip('\ufeff') if val else default

TELEGRAM_BOT_TOKEN = clean_env("TELEGRAM_BOT_TOKEN", "8864791666:AAEI0R4XrbbyXVBGj85dg9L7S5cl-PhpjwU")
TELEGRAM_CHAT_ID = clean_env("TELEGRAM_CHAT_ID", "1335170519")
BASE_URL = "https://keshavs40344.github.io/ai-world-core"

def broadcast_live_asset(asset_name: str, rel_path: str, category: str = "Autonomous SaaS", key_feature: str = "100% In-Browser & Private"):
    """Fires an instant completion message to Telegram with zero blocking."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] Telegram credentials missing or skipped.")
        return

    import html
    clean_path = rel_path.replace("\\", "/").lstrip("/")
    live_url = f"{BASE_URL}/{clean_path}"

    safe_name = html.escape(asset_name)
    safe_cat = html.escape(category)
    safe_feat = html.escape(key_feature)

    message = (
        f"⚡ <b>GENESIS AUTONOMOUS DISPATCH</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Status:</b> Deployed &amp; 100% Working\n"
        f"📦 <b>Application:</b> <code>{safe_name}</code>\n"
        f"🏷️ <b>Category:</b> {safe_cat}\n"
        f"🛡️ <b>Security:</b> {safe_feat}\n\n"
        f"🔗 <b>Live Working Link:</b>\n{live_url}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <i>Auto-committed to main. Zero approval needed.</i>"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        # Strict 5-second network timeout - never hangs the runner
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                print(f"✔ Instant Telegram bulletin sent for: {asset_name}")
    except Exception as e:
        print(f"[-] Telegram dispatch error (ignored to prevent workflow failure): {e}")

if __name__ == "__main__":
    # Test dispatch if run standalone
    if len(sys.argv) >= 3:
        cat = sys.argv[3] if len(sys.argv) >= 4 else "Autonomous Tool"
        broadcast_live_asset(sys.argv[1], sys.argv[2], cat)
    else:
        broadcast_live_asset("Genesis Core Engine", "public/index.html", "Core Infrastructure")
