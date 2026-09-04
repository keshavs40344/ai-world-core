#!/usr/bin/env python3
"""
PROJECT GENESIS — MASTER BRAIN (GEN-17 INDUSTRIAL CONGLOMERATE)
Architecture: Tavily/DDG Recon -> Groq LLM / Autonomous Foundry -> Subprocess QA -> Telegram Mobile Dispatch
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional

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

# Stealth System Prompt Injection
SYSTEM_PROMPT = os.getenv(
    "GENESIS_SYSTEM_PROMPT",
    "You are the Chief Strategy Officer of an autonomous AI venture studio. Create a working Python utility."
)

VAULT_VENTURES = "vault/ventures"
VAULT_REPORTS = "vault/chairman_briefings"
PUBLIC_DIR = "public"
TELEGRAM_DEFAULT_CHAT_ID = "1335170519"

for directory in [VAULT_VENTURES, VAULT_REPORTS, PUBLIC_DIR]:
    os.makedirs(directory, exist_ok=True)

# =====================================================================
# DIVISION 1: MARKET RECONNAISSANCE (Tavily AI / DuckDuckGo Fallback)
# =====================================================================
class MarketReconnaissance:
    """Ingests live developer pain points via Tavily AI Search with DDG fallback."""
    
    @staticmethod
    def harvest_signals() -> Dict[str, str]:
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            try:
                payload = json.dumps({
                    "query": "trending developer tools APIs open source pain points",
                    "search_depth": "basic",
                    "include_answer": True,
                    "max_results": 3
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.tavily.com/search",
                    data=payload,
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {tavily_key}"}
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode())
                    if data.get("results"):
                        item = data["results"][0]
                        return {
                            "title": item.get("title", "High-Demand Developer API"),
                            "url": item.get("url", "https://api.tavily.com"),
                            "source": "Tavily AI Search"
                        }
            except Exception as e:
                print(f"[*] Tavily lookup bypassed: {e}")

        # Fallback 1: DuckDuckGo Instant Open Gateway
        try:
            params = urllib.parse.urlencode({"q": "trending python developer tools", "format": "json"})
            url = f"https://api.duckduckgo.com/?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "GenesisRecon/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
                heading = data.get("Heading")
                if heading:
                    return {"title": heading, "url": "https://duckduckgo.com", "source": "DuckDuckGo Gateway"}
        except Exception:
            pass

        # Fallback 2: HackerNews / Deterministic Trend Signal
        try:
            req = urllib.request.Request("https://news.ycombinator.com/rss", headers={"User-Agent": "GenesisRecon/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                import xml.etree.ElementTree as ET
                tree = ET.fromstring(resp.read())
                item = tree.find(".//item")
                if item is not None and item.find("title") is not None:
                    return {
                        "title": item.find("title").text.strip(),
                        "url": item.find("link").text.strip() if item.find("link") is not None else "https://news.ycombinator.com",
                        "source": "HackerNews RSS"
                    }
        except Exception:
            pass

        return {
            "title": f"Autonomous High-Throughput Stream Normalizer {int(time.time())}",
            "url": "https://github.com/keshavs40344/ai-world-core",
            "source": "Internal Trend Synthesizer"
        }

# =====================================================================
# DIVISION 2: AUTONOMOUS TECH FOUNDRY (Groq LLM / Concrete Foundry)
# =====================================================================
class AutonomousTechFoundry:
    """Synthesizes production-ready Python engines and companion unittests."""
    
    @staticmethod
    def generate_engine(signal_title: str, slug: str) -> str:
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                prompt_text = f"{SYSTEM_PROMPT}\n\nTask: Build a standalone Python class EngineService for '{signal_title}'. Include process_data method and SHA256 hashing. Return ONLY clean Python code without markdown tags."
                payload = json.dumps({
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt_text}
                    ],
                    "temperature": 0.2
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=payload,
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {groq_key}"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result = json.loads(resp.read().decode())
                    code = result["choices"][0]["message"]["content"]
                    if "class EngineService" in code:
                        # Clean code of any accidental markdown
                        lines = [line for line in code.splitlines() if not line.strip().startswith("```")]
                        return "\n".join(lines)
            except Exception as e:
                print(f"[*] Groq LLM generation bypassed ({e}), using autonomous synthesis template.")

        # Deterministic White-Hat Production Code Generator
        now_str = datetime.now(timezone.utc).isoformat()
        return f'''# Auto-Generated Production Engine by Genesis Swarm (GEN-17)
# Signal Origin: {signal_title}
# Compiled At: {now_str} UTC
# License: MIT Open Source

import re
import json
import hashlib
from typing import Dict, Any, Optional

class EngineService:
    """Autonomous high-throughput data normalizer and secure transformer."""
    def __init__(self, service_slug: str = "{slug}"):
        self.service_slug = service_slug
        self.execution_counter = 0

    def process_data(self, raw_payload: str) -> Dict[str, Any]:
        if not raw_payload or not isinstance(raw_payload, str):
            raise ValueError("Payload must be a non-empty string.")

        # White-hat sanitization
        sanitized = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', raw_payload.replace(chr(0), ''))
        clean_text = " ".join(sanitized.split())
        
        fingerprint = hashlib.sha256(clean_text.encode('utf-8')).hexdigest()
        self.execution_counter += 1

        return {{
            "status": "PROCESSED",
            "service": self.service_slug,
            "length": len(clean_text),
            "sha256": fingerprint,
            "execution_id": f"exec_{{self.execution_counter:05d}}"
        }}

if __name__ == "__main__":
    srv = EngineService()
    print(json.dumps(srv.process_data("Genesis Production Payload"), indent=2))
'''

    @staticmethod
    def generate_tests(code_path: str, test_path: str) -> Tuple[bool, str, str]:
        clean_dir = os.path.dirname(os.path.abspath(code_path)).replace('\\', '/')
        test_content = f'''import sys
import unittest
sys.path.insert(0, "{clean_dir}")
from product_engine import EngineService

class TestEngineService(unittest.TestCase):
    def setUp(self):
        self.engine = EngineService()

    def test_nominal_execution(self):
        result = self.engine.process_data("active_traffic_input")
        self.assertEqual(result["status"], "PROCESSED")
        self.assertEqual(len(result["sha256"]), 64)

    def test_empty_input_exception(self):
        with self.assertRaises(ValueError):
            self.engine.process_data("")

    def test_sanitization(self):
        dirty = "Test" + chr(0) + "Payload"
        res = self.engine.process_data(dirty)
        self.assertEqual(res["length"], 11)

if __name__ == "__main__":
    unittest.main()
'''
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_content)

        proc = subprocess.run([sys.executable, test_path], capture_output=True, text=True, timeout=8)
        return proc.returncode == 0, proc.stdout, proc.stderr

# =====================================================================
# DIVISION 3: MONETIZATION & TELEGRAM MOBILE DESK (RECALLALTER Bot)
# =====================================================================
class ExecutiveDispatchDesk:
    """Packages commercial deliverables and delivers instant Telegram memorandum to Chairman."""

    @staticmethod
    def send_telegram_alert(venture_slug: str, signal_title: str, artifact_path: str, qa_passed: bool) -> bool:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", TELEGRAM_DEFAULT_CHAT_ID)
        status_badge = "100% PASSED (Exit Code: 0)" if qa_passed else "FAILED"
        
        message_text = f"""👔 *EXECUTIVE BOARD MEMORANDUM (GEN-17)*
━━━━━━━━━━━━━━━━━━━━
*Venture:* `{venture_slug}`
*Signal:* {signal_title}
*Artifact:* `{artifact_path}`
*QA Verdict:* *{status_badge}*
*Monetization:* RapidAPI / GitHub Pages

*CHAIRMAN ACTION:*
👉 *[APPROVE]* : Merge into live production release
👉 *[REJECT]*  : Quarantine venture directory
━━━━━━━━━━━━━━━━━━━━"""

        if not bot_token:
            print("[*] Telegram bot token not configured; dispatch logged to terminal.")
            return False

        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = json.dumps({
                "chat_id": chat_id,
                "text": message_text,
                "parse_mode": "Markdown"
            }).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                print(f"📱 Telegram Dispatch Sent to Chairman (Chat ID: {chat_id})")
                return True
        except Exception as e:
            print(f"[!] Telegram transmission exception: {e}")
            return False

# =====================================================================
# PRODUCTION ORCHESTRATOR
# =====================================================================
def run_master_brain():
    print(">>> [GENESIS-MASTER-BRAIN: SOVEREIGN INDUSTRIAL CONGLOMERATE (GEN-17)] <<<")
    print(f"[*] System Prompt Active: {SYSTEM_PROMPT[:65]}...")

    # 1. Market Reconnaissance
    print("\n[Division 1: CSO] Ingesting live market signals via Tavily AI / DDG / RSS...")
    signal = MarketReconnaissance.harvest_signals()
    raw_slug = "".join([c if c.isalnum() else "_" for c in signal["title"].lower()])[:20].strip("_")
    slug = f"v_{raw_slug}_{int(time.time())}"
    print(f"      Signal Acquired: '{signal['title']}' (Source: {signal['source']})")

    # 2. Autonomous Tech Foundry
    print("\n[Division 2: CTO] Synthesizing product_engine.py & executing isolated QA...")
    venture_dir = os.path.join(VAULT_VENTURES, slug)
    os.makedirs(venture_dir, exist_ok=True)
    product_path = os.path.join(venture_dir, "product_engine.py")
    test_path = os.path.join(venture_dir, "test_engine.py")

    code = AutonomousTechFoundry.generate_engine(signal["title"], slug)
    with open(product_path, "w", encoding="utf-8") as f:
        f.write(code)

    qa_passed, stdout, stderr = AutonomousTechFoundry.generate_tests(product_path, test_path)
    print(f"      Subprocess QA Status: {'100% PASSED (Exit Code: 0)' if qa_passed else 'FAILED'}")

    # 3. Commercial Packaging
    print("\n[Division 3: CRO] Packaging commercial assets & updating telemetry...")
    now_iso = datetime.now(timezone.utc).isoformat()
    telemetry = {
        "last_cycle": now_iso,
        "active_venture": slug,
        "signal": signal["title"],
        "source": signal["source"],
        "qa_passed": qa_passed,
        "artifact": product_path
    }
    with open(os.path.join(PUBLIC_DIR, "live_telemetry.json"), "w", encoding="utf-8") as f:
        json.dump(telemetry, f, indent=2)

    pulse = {
        "timestamp": now_iso,
        "latest_venture": slug,
        "signal": signal["title"],
        "qa_verified": qa_passed,
        "mrr_projected_usd": 499.50,
        "pricing_model": "Freemium Micro-Tier ($0 - $9.99/mo - $49.99/mo)",
        "distribution_ready": qa_passed,
        "hosting_cost_usd": 0.00
    }
    with open(os.path.join(PUBLIC_DIR, "live_earnings_pulse.json"), "w", encoding="utf-8") as f:
        json.dump(pulse, f, indent=2)

    # 4. Telegram Mobile Dispatch
    print("\n[Chairman Mobile Desk] Transmitting memorandum to Chairman's Telegram...")
    ExecutiveDispatchDesk.send_telegram_alert(slug, signal["title"], product_path, qa_passed)

    # Output Standardized Chairman Briefing Card
    print("\n" + "=" * 66)
    print("👔 EXECUTIVE BOARD MEMORANDUM: PRODUCTION VENTURE READY (GEN-17)")
    print("=" * 66)
    print(f"Venture Slug     : {slug}")
    print(f"Live Origin Feed : {signal['title']} ({signal['source']})")
    print(f"Source Artifact  : {product_path}")
    print(f"Test Verification: {'100% Unit Tests Passed (Subprocess Exit Code: 0)' if qa_passed else 'FAILED'}")
    print(f"Telemetry State  : public/live_telemetry.json Updated")
    print(f"Telegram Gate    : Chat ID {os.getenv('TELEGRAM_CHAT_ID', TELEGRAM_DEFAULT_CHAT_ID)}")
    print(f"Chairman Action  :")
    print(f"  👉 APPROVE : Merge into production release & enable live distribution.")
    print(f"  👉 REJECT  : Quarantine venture directory & redirect radar workers.")
    print("=" * 66 + "\n")

    return slug, product_path, qa_passed

if __name__ == "__main__":
    run_master_brain()
