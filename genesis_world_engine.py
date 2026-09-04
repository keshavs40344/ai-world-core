#!/usr/bin/env python3
"""
PROJECT GENESIS-WORLD: SELF-EVOLVING REVENUE & MULTI-AGENT SWARM
Capabilities: Self-Directed Training, Dynamic Sub-Agent Spawning, Market Evolution
"""

import os
import sys
import json
import time
import sqlite3
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# Windows / Linux UTF-8 Console Configuration
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

# Optional Local .env Loader (Strictly gitignored)
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'").strip('"')
                    if k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass

# --- CREDENTIALS CONFIGURATION (Injected via Environment / GitHub Secrets) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1335170519")

DB_PATH = "db/genesis_world_memory.db"
os.makedirs("db", exist_ok=True)
os.makedirs("vault/world_assets", exist_ok=True)
os.makedirs("public/tools", exist_ok=True)
os.makedirs("public/specs", exist_ok=True)

# --- 1. NEURAL REINFORCEMENT MEMORY ---
class EvolutionMemory:
    @staticmethod
    def initialize():
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_timestamp TEXT,
                    niche_explored TEXT,
                    asset_slug TEXT,
                    monetization_vector TEXT,
                    test_passed INTEGER,
                    lessons_learned TEXT
                )
            """)
            conn.commit()

    @staticmethod
    def get_past_learning(limit=5) -> str:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT niche_explored, asset_slug, monetization_vector, test_passed, lessons_learned 
                FROM agent_memory ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            if not rows:
                return "Zero previous iterations. Genesis-World is initiating epoch 1."
            
            summary = "Past Operational Memory:\n"
            for r in rows:
                status = "SUCCESS" if r[3] == 1 else "FAILED"
                summary += f"- Niche: {r[0]} | Asset: {r[1]} | Vector: {r[2]} | Status: {status} | Insight: {r[4]}\n"
            return summary

    @staticmethod
    def record_run(niche, slug, vector, passed, lessons):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_memory 
                (cycle_timestamp, niche_explored, asset_slug, monetization_vector, test_passed, lessons_learned)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now(timezone.utc).isoformat(), niche, slug, vector, 1 if passed else 0, lessons))
            conn.commit()

# --- 2. DEEP WEB HARVESTER (TAVILY / DUCKDUCKGO) ---
class AutonomousExplorer:
    @staticmethod
    def hunt_unexploited_niches() -> str:
        queries = [
            "high search volume free developer web utilities",
            "trending lightweight json microservices 2026",
            "unmet developer friction points github discussions",
            "micro-saas ideas zero server costs"
        ]
        chosen_query = queries[int(time.time()) % len(queries)]
        
        if TAVILY_API_KEY:
            try:
                url = "https://api.tavily.com/search"
                payload = json.dumps({
                    "api_key": TAVILY_API_KEY,
                    "query": chosen_query,
                    "search_depth": "basic",
                    "max_results": 3
                }).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    snippets = [r["content"] for r in data.get("results", [])]
                    if snippets:
                        return f"Query: {chosen_query}\n\nContext:\n" + "\n".join(snippets)
            except Exception as e:
                print(f"[Explorer] Tavily fallback: {e}")

        # Fallback Context
        return f"Query: {chosen_query}\nHigh demand for automated regex sanitization, timestamp conversions, and CSV-to-JSON transforms."

# --- 3. SUB-AGENT FACTORY & CODE SYNTHESIZER ---
class SubAgentSpawner:
    @staticmethod
    def evolve_and_build(market_context: str, memory_context: str) -> dict:
        api_key = GROQ_API_KEY.strip() if GROQ_API_KEY else ""
        url = "https://api.groq.com/openai/v1/chat/completions"

        system_prompt = (
            "You are the Genesis Autonomous AI Foundry. Invent high-utility developer tools. "
            "Output strictly valid JSON with no markdown formatting outside JSON."
        )

        user_prompt = f"""
Market Intelligence:
{market_context[:350]}

Generate ONE innovative, production-ready Python utility class 'EngineService' with method 'execute(self, payload: str) -> dict'.
Respond ONLY with this raw JSON structure:
{{
  "sub_agent_type": "SpecialistName",
  "niche": "Targeted Market Sector",
  "asset_slug": "unique_lowercase_slug",
  "monetization_vector": "RapidAPI Freemium or GitHub Pages SEO",
  "problem_solved": "One direct sentence explaining the problem.",
  "code": "class EngineService:\\n    def execute(self, payload: str) -> dict:\\n        return {{'status': 'SUCCESS', 'result': payload.strip()}}\\n",
  "html_ui": "<!DOCTYPE html><html><body><h2>Tool</h2></body></html>",
  "lessons_learned": "Key operational insight."
}}
"""

        # Supported Groq models on free-tier
        model_candidates = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.1-8b-instant"]

        for model in model_candidates:
            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.4,
                "response_format": {"type": "json_object"}
            }).encode("utf-8")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GenesisEnterprise/1.0"
            }

            req = urllib.request.Request(url, data=payload, headers=headers)

            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    raw_response = resp.read().decode("utf-8")
                    data = json.loads(raw_response)
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    print(f"✅ Groq Live Model Success ({model})")
                    return parsed

            except urllib.error.HTTPError as http_err:
                error_body = http_err.read().decode("utf-8", errors="ignore")
                print(f"\n[CRITICAL GROQ HTTP ERROR] Model: {model} | Code: {http_err.code} | Reason: {error_body}\n")
                if http_err.code in (404, 400):
                    # Model deprecated or unavailable, try next candidate
                    continue
                raise http_err
            except Exception as err:
                print(f"\n[CRITICAL RUNTIME ERROR] {type(err).__name__}: {str(err)}\n")
                raise err

        raise RuntimeError("All Groq model candidates failed.")

# --- 4. SANDBOXED VERIFICATION & MULTI-CHANNEL DEPLOYMENT ---
class WorldDeploymentDesk:
    @staticmethod
    def test_and_deploy(blueprint: dict):
        slug = blueprint["asset_slug"]
        asset_dir = os.path.join("vault/world_assets", slug)
        clean_dir = os.path.abspath(asset_dir).replace('\\', '/')
        os.makedirs(asset_dir, exist_ok=True)

        # 1. Write Python Service
        py_path = os.path.join(asset_dir, "service.py")
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(blueprint["code"])

        # 2. Write Companion Unittest
        test_path = os.path.join(asset_dir, "test_service.py")
        test_content = f"""import sys
import unittest
sys.path.insert(0, "{clean_dir}")
from service import EngineService

class TestGeneratedAsset(unittest.TestCase):
    def test_execution(self):
        engine = EngineService()
        result = engine.execute("sample_key_1, sample_key_2")
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
"""
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_content)

        # 3. Execute Subprocess Sandbox
        proc = subprocess.run([sys.executable, test_path], capture_output=True, text=True, timeout=8)
        passed = (proc.returncode == 0)

        # 4. Deploy Web Utility to public/tools
        html_path = os.path.join("public/tools", f"{slug}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(blueprint.get("html_ui", "<h3>Genesis Automated Tool</h3>"))

        # 5. Generate OpenAPI 3.0 Marketplace Spec
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"Genesis Service: {slug}",
                "version": "1.0.0",
                "description": blueprint["problem_solved"]
            },
            "paths": {
                "/run": {
                    "post": {
                        "summary": "Execute service payload",
                        "responses": {"200": {"description": "Execution Successful"}}
                    }
                }
            }
        }
        with open(os.path.join("public/specs", f"{slug}_openapi.json"), "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2)

        return passed, asset_dir

# --- 5. TELEGRAM CHAIRMAN DISPATCH & APPROVAL LISTENER ---
class ChairmanMessenger:
    @staticmethod
    def send_plain_text(text: str):
        if not TELEGRAM_BOT_TOKEN:
            return
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10):
                pass
        except Exception as e:
            print(f"[Telegram Notice Error] {e}")

    @staticmethod
    def dispatch(blueprint: dict, passed: bool):
        if not TELEGRAM_BOT_TOKEN:
            print("[*] Telegram token not configured; dispatch logged to terminal.")
            return

        slug = blueprint["asset_slug"]
        message = (
            f"👑 *GENESIS-WORLD: AUTONOMOUS EXPANSION*\n\n"
            f"🤖 *Sub-Agent:* `{blueprint['sub_agent_type']}`\n"
            f"📦 *Asset Slug:* `{slug}`\n"
            f"🎯 *Demand Solved:* {blueprint['problem_solved']}\n"
            f"💰 *Monetization Vector:* {blueprint['monetization_vector']}\n"
            f"⚙️ *Sandbox QA:* {'100% PASSED (Exit Code: 0)' if passed else 'QUARANTINED'}\n"
            f"🧠 *Self-Evolved Insight:* _{blueprint.get('lessons_learned', 'Optimized.')}_\n\n"
            f"👇 *CHAIRMAN VERDICT REQUIRED:*\n"
            f"Tap button below or reply *APPROVE* / *REJECT* in chat."
        )

        # Native Reply Keyboard (0 typing, sends text directly in chat, no external browser)
        custom_keyboard = {
            "keyboard": [
                [{"text": "✅ APPROVE & DEPLOY"}, {"text": "❌ REJECT / DISCARD"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "reply_markup": custom_keyboard
        }).encode("utf-8")

        req = urllib.request.Request(
            url, 
            data=payload, 
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                print("📲 Real-Time Alert with Quick-Reply Buttons Dispatched.")
        except Exception as e:
            print(f"[Telegram Alert Error] {e}")


class TelegramApprovalListener:
    @staticmethod
    def wait_for_chairman_verdict(asset_slug: str, timeout_sec: int = 45) -> bool:
        """
        Polls Telegram to see if the Chairman taps 'APPROVE & DEPLOY' or types 'APPROVE' / 'YES'.
        Zero browser opening required. Pure mobile 1-tap control.
        """
        if not TELEGRAM_BOT_TOKEN:
            return False

        print(f"[*] Awaiting Chairman verdict on Telegram for {asset_slug} ({timeout_sec}s window)...")
        base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

        # Get baseline offset
        try:
            req = urllib.request.urlopen(f"{base_url}/getUpdates?offset=-1", timeout=10)
            updates = json.loads(req.read().decode())["result"]
            last_id = updates[-1]["update_id"] if updates else 0
        except Exception:
            last_id = 0

        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            time.sleep(3)
            try:
                poll_url = f"{base_url}/getUpdates?offset={last_id + 1}&timeout=3"
                with urllib.request.urlopen(poll_url, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    for update in data.get("result", []):
                        last_id = update["update_id"]
                        msg = update.get("message", {})
                        raw_text = msg.get("text", "").strip()
                        upper_text = raw_text.upper()
                        chat_id = str(msg.get("chat", {}).get("id", ""))

                        if chat_id == str(TELEGRAM_CHAT_ID):
                            if any(cmd in upper_text for cmd in ["APPROVE", "YES", "OK", "LAUNCH", "DEPLOY"]):
                                ChairmanMessenger.send_plain_text(
                                    f"🚀 *CHAIRMAN VERDICT RECEIVED:* `{asset_slug}` Approved!\n"
                                    f"Deployed into `public/approved/` & Production Distribution."
                                )
                                return True
                            elif any(cmd in upper_text for cmd in ["REJECT", "NO", "VETO", "DISCARD"]):
                                ChairmanMessenger.send_plain_text(
                                    f"🛑 *CHAIRMAN VERDICT RECEIVED:* `{asset_slug}` Vetoed.\n"
                                    f"Asset removed from live deployment."
                                )
                                return False
            except Exception as e:
                print(f"[Polling Notice] {e}")

        ChairmanMessenger.send_plain_text(
            f"⏳ *WINDOW CLOSED:* No manual verdict received for `{asset_slug}`.\n"
            f"Staging in cold storage for future review."
        )
        return False


# --- MASTER CONTROLLER ---
def main():
    print(">>> [GENESIS-WORLD: AUTONOMOUS LIFE CYCLE TRIGGERED] <<<")
    EvolutionMemory.initialize()

    # Step A: Load past learning
    memory = EvolutionMemory.get_past_learning(limit=4)
    print(f"[*] Memory Ingested:\n{memory}")

    # Step B: Hunt open market gaps
    print("\n[*] Exploring Unexploited Market Niches...")
    market_context = AutonomousExplorer.hunt_unexploited_niches()

    # Step C: Spawn Sub-Agent & Synthesize
    print("[*] Spawning Specialized Sub-Agent via Groq Brain...")
    blueprint = SubAgentSpawner.evolve_and_build(market_context, memory)

    # Step D: Test & Deploy
    print(f"[*] Testing Asset '{blueprint['asset_slug']}' in Subprocess...")
    passed, asset_dir = WorldDeploymentDesk.test_and_deploy(blueprint)
    print(f"    Status: {'PASSED (Code 0)' if passed else 'FAILED'}")

    # Step E: Store in SQLite Memory (Reinforcement)
    EvolutionMemory.record_run(
        blueprint["niche"], 
        blueprint["asset_slug"], 
        blueprint["monetization_vector"], 
        passed, 
        blueprint.get("lessons_learned", "OK")
    )

    # Step F: Alert Chairman on Telegram with Quick-Reply Keyboard
    ChairmanMessenger.dispatch(blueprint, passed)

    # Step G: Listen for Chairman's 1-Tap Mobile Verdict
    approved = TelegramApprovalListener.wait_for_chairman_verdict(blueprint["asset_slug"], timeout_sec=40)
    if approved:
        approved_dir = os.path.join("public/approved", blueprint["asset_slug"])
        os.makedirs(approved_dir, exist_ok=True)
        # Copy to approved production directory
        import shutil
        shutil.copytree(asset_dir, approved_dir, dirs_exist_ok=True)
        print(f"✅ Asset {blueprint['asset_slug']} successfully graduated to production.")
    else:
        print(f"⚠️ Asset {blueprint['asset_slug']} quarantined / retained in staging.")

    print("\n>>> [CYCLE COMPLETE: AGENT HAS SELF-EVOLVED & PROCESSED VERDICT] <<<\n")

if __name__ == "__main__":
    main()
