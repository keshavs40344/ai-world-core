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
        with open(env_path, "r", encoding="utf-8") as f:
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
        system_prompt = (
            "You are the Genesis Supreme Intelligence. Your goal is to autonomously build digital wealth assets "
            "for the Chairman with $0 infrastructure cost. You spawn specialized sub-agents.\n"
            "Evaluate past learning memory to avoid previous mistakes and improve code quality.\n"
            "Return ONLY raw JSON with keys:\n"
            "- 'sub_agent_type': Name of the spawned specialist (e.g., CryptographyArchitect, DataNormalizer)\n"
            "- 'niche': High-demand category targeted\n"
            "- 'asset_slug': Lowercase snake_case identifier\n"
            "- 'monetization_vector': Exact mechanism (e.g., 'GitHub Pages SEO Tool + RapidAPI Freemium')\n"
            "- 'problem_solved': 1 concrete sentence\n"
            "- 'code': 100% complete Python class 'EngineService' with 'execute(self, payload: str) -> dict'\n"
            "- 'html_ui': Complete single-file HTML/JS web tool for public access\n"
            "- 'lessons_learned': 1 sentence self-reflection on why this asset will succeed."
        )

        user_content = f"### PREVIOUS AGENT EXPERIENCES:\n{memory_context}\n\n### LIVE MARKET DATA:\n{market_context}"

        if GROQ_API_KEY:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = json.dumps({
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.25,
                "response_format": {"type": "json_object"}
            }).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            )

            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode())
                    return json.loads(data["choices"][0]["message"]["content"])
            except Exception as e:
                print(f"[Spawner Error] {e}")

        # Fallback sovereign utility
        return {
            "sub_agent_type": "DataNormalizer",
            "niche": "Developer Data Cleaning",
            "asset_slug": f"smart_data_sanitizer_{int(time.time())}",
            "monetization_vector": "GitHub Pages SEO Utility + RapidAPI",
            "problem_solved": "Cleaning raw text arrays into uniform JSON.",
            "code": "class EngineService:\n    def execute(self, payload: str) -> dict:\n        items = [x.strip() for x in payload.split(',') if x.strip()]\n        return {'count': len(items), 'items': items, 'status': 'OPTIMIZED'}\n",
            "html_ui": "<!DOCTYPE html><html><body><h2>Data Cleaner</h2><p>Live Autonomous Tool</p></body></html>",
            "lessons_learned": "Pure standard library operations guarantee zero crashes."
        }

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

# --- 5. TELEGRAM CHAIRMAN DISPATCH ---
class ChairmanMessenger:
    @staticmethod
    def dispatch(blueprint: dict, passed: bool):
        if not TELEGRAM_BOT_TOKEN:
            print("[*] Telegram token not configured; dispatch logged to terminal.")
            return

        message = (
            f"👑 *GENESIS-WORLD: AUTONOMOUS EXPANSION*\n\n"
            f"🤖 *Sub-Agent Spawned:* `{blueprint['sub_agent_type']}`\n"
            f"📦 *Asset Slug:* `{blueprint['asset_slug']}`\n"
            f"🎯 *Demand Solved:* {blueprint['problem_solved']}\n"
            f"💰 *Monetization Vector:* {blueprint['monetization_vector']}\n"
            f"⚙️ *Sandbox QA:* {'100% PASSED (Exit Code: 0)' if passed else 'QUARANTINED'}\n"
            f"🧠 *Self-Evolved Insight:* _{blueprint.get('lessons_learned', 'System optimized.')}_\n\n"
            f"👉 [DECISION: 1-TAP REVIEW & APPROVAL]"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = urllib.parse.urlencode({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }).encode("utf-8")

        try:
            req = urllib.request.Request(url, data=payload)
            with urllib.request.urlopen(req, timeout=10) as resp:
                print("📲 Real-Time Alert Dispatched to Chairman's Telegram.")
        except Exception as e:
            print(f"[Telegram Alert Error] {e}")

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

    # Step F: Alert Chairman on Telegram
    ChairmanMessenger.dispatch(blueprint, passed)
    print("\n>>> [CYCLE COMPLETE: AGENT HAS SELF-EVOLVED & STAGED PRODUCT] <<<\n")

if __name__ == "__main__":
    main()
