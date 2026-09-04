#!/usr/bin/env python3
"""
GENESIS AGENT MERCURY: AUTONOMOUS WEBHOOK BROADCASTER
Parses distribution packages from public/outreach/ and broadcasts release
announcements to external developer channels via webhooks and Telegram feeds.
"""

import os
import sys
import glob
import json
import sqlite3
import urllib.request
from datetime import datetime, timezone

# UTF-8 Console encoding safety
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DB_PATH = "db/distribution_ledger.db"
os.makedirs("db", exist_ok=True)
os.makedirs("public/outreach", exist_ok=True)

def clean_env(key: str, default: str = "") -> str:
    val = os.getenv(key, default)
    return val.strip().lstrip('\ufeff') if val else default

TELEGRAM_BOT_TOKEN = clean_env("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = clean_env("TELEGRAM_CHAT_ID", "1335170519")
DISCORD_WEBHOOK_URL = clean_env("DISCORD_WEBHOOK_URL", "")

class MercuryBroadcaster:
    @staticmethod
    def init_ledger():
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS broadcast_history (
                    slug TEXT PRIMARY KEY,
                    title TEXT,
                    channel TEXT,
                    broadcasted_at TEXT
                )
            """)
            conn.commit()

    @classmethod
    def run_distribution_cycle(cls):
        cls.init_ledger()
        print("[AGENT MERCURY] Scanning outbound marketing packs...")

        packs = glob.glob("public/outreach/*_campaign.json")
        dispatched = 0

        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            for pack_path in packs:
                with open(pack_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except Exception:
                        continue

                slug = data.get("asset_slug", "")
                cur.execute("SELECT slug FROM broadcast_history WHERE slug = ?", (slug,))
                if cur.fetchone():
                    continue  # Already distributed

                cls._dispatch_announcement(data)
                cur.execute(
                    "INSERT INTO broadcast_history VALUES (?, ?, 'Multi-Channel', ?)",
                    (slug, data.get("title", ""), datetime.now(timezone.utc).isoformat())
                )
                conn.commit()
                dispatched += 1

        print(f"[MERCURY BROADCAST] Cycle complete: {dispatched} new assets dispatched to feeds.")

    @classmethod
    def _dispatch_announcement(cls, pack: dict):
        title = pack.get("title", "New Utility")
        url = pack.get("live_url", "")
        hook = pack.get("distribution_channels", {}).get("reddit_pitch", "")

        # 1. Telegram Channel / Chairman Dispatch
        if TELEGRAM_BOT_TOKEN:
            msg = (
                f"📢 *MERCURY AUTONOMOUS BROADCAST*\n\n"
                f"🚀 *Shipped Asset:* `{title}`\n"
                f"🌐 *Live Link:* {url}\n\n"
                f"🎯 *Pitch Copy:*\n_{hook}_\n\n"
                f"⚡ *Distributed to public search indexing and feed monitors.*"
            )
            t_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}).encode("utf-8")
            try:
                req = urllib.request.Request(t_url, data=payload, headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=10)
            except Exception:
                pass

        # 2. Discord Webhook Push (if token exists)
        if DISCORD_WEBHOOK_URL:
            d_payload = json.dumps({
                "content": f"🚀 **New Autonomous Release:** **{title}**\n{hook}\n🔗 Access: {url}"
            }).encode("utf-8")
            try:
                d_req = urllib.request.Request(DISCORD_WEBHOOK_URL, data=d_payload, headers={"Content-Type": "application/json"})
                urllib.request.urlopen(d_req, timeout=10)
            except Exception:
                pass

if __name__ == "__main__":
    MercuryBroadcaster.run_distribution_cycle()
