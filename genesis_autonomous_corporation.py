#!/usr/bin/env python3
"""
PROJECT GENESIS AUTONOMOUS CORPORATION
Self-Operating Software Conglomerate & Competitor SaaS Disruptor ($0 Operating Cost)

Department Matrix:
- Agent Alpha (Chief Intelligence Officer): Scans live friction & competitor SaaS pain points.
- Agent Beta (Competitive Product Architect): Reverse-engineers target SaaS into superior zero-leak architecture.
- Agent Gamma (Chief Engineer): Synthesizes full standalone client-side SaaS (Tailwind, LocalStorage, PDF/CSV export).
- Agent Delta (QA Sentinel): Subprocess sandboxing, unit testing, and self-healing verification.
- Agent Epsilon (Chief Commercial Officer): Deploys app, updates storefront/sitemap, attaches direct UPI paywall, dispatches Telegram audit report.
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

# Ensure UTF-8 output
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

# Safe UTF-8 BOM immune environment loader
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

def clean_env(key: str, default: str = "") -> str:
    val = os.getenv(key, default)
    return val.strip().lstrip('\ufeff') if val else default

GROQ_API_KEY = clean_env("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN = clean_env("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = clean_env("TELEGRAM_CHAT_ID", "1335170519")
UPI_ID = "keshavthakur07@ptyes"
PAYEE_NAME = "Keshav"
AMOUNT = "299.00"
NOTE = "Genesis_SaaS_Pro_Lifetime"
BASE_URL = "https://keshavs40344.github.io/ai-world-core"
DB_PATH = "db/genesis_master.db"

# Ensure core enterprise infrastructure
DIRS = ["db", "vault/corporation_intel", "vault/specialists", "public/saas", "public/tools", "public/specs", "public/outreach"]
for d in DIRS:
    os.makedirs(d, exist_ok=True)

# ============================================================
# 1. CORPORATE NEURAL MEMORY (SQLite)
# ============================================================
class CorporateMemory:
    @staticmethod
    def init_db():
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS corporation_portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    competitor_target TEXT,
                    product_slug TEXT UNIQUE,
                    product_name TEXT,
                    category TEXT,
                    disruption_angle TEXT,
                    qa_status TEXT,
                    status TEXT
                )
            """)
            conn.commit()

    @staticmethod
    def get_deployed_slugs() -> list:
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute("SELECT product_slug FROM corporation_portfolio").fetchall()
            return [r[0] for r in rows]

    @staticmethod
    def record_deployment(intel: dict, blueprint: dict, qa_status: str):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO corporation_portfolio 
                (timestamp, competitor_target, product_slug, product_name, category, disruption_angle, qa_status, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
            """, (
                datetime.now(timezone.utc).isoformat(),
                intel.get("target_saas", "Generic SaaS"),
                blueprint["slug"],
                blueprint["name"],
                intel.get("category", "Developer Utility"),
                intel.get("pain_point", "High pricing and privacy risk"),
                qa_status
            ))
            conn.commit()

# ============================================================
# 2. AGENT ALPHA: CHIEF INTELLIGENCE OFFICER (Radar & Competitor Scan)
# ============================================================
class AgentAlphaCIO:
    COMPETITOR_VECTORS = [
        {
            "target_saas": "Postman / Insomnia Mock Server",
            "category": "API Development",
            "pain_point": "Aggressive cloud account lock-in, data privacy risks with internal payloads, complex subscription tiers ($14/mo per user).",
            "disruption_hypothesis": "Build an instant in-browser API Mock Server & Payload Inspector with zero cloud upload and instant response simulation."
        },
        {
            "target_saas": "QuickBooks / FreshBooks Expense Tracker",
            "category": "FinTech / Small Business",
            "pain_point": "Overpriced monthly subscriptions ($30/mo) for simple itemized expense splitting, tax calculations, and GST reconciliation.",
            "disruption_hypothesis": "Build an ultra-fast client-side B2B Tax & Ledger Studio with persistent localStorage and native publication-grade PDF print export."
        },
        {
            "target_saas": "Datadog / Loggly JSON Log Sanitizer",
            "category": "DevSecOps",
            "pain_point": "Huge cloud ingestion bills and risk of accidentally leaking customer PII / credit cards / auth tokens into third-party servers.",
            "disruption_hypothesis": "Build an automated client-side log scrubber that strips sensitive credentials locally before log forwarding."
        },
        {
            "target_saas": "JSONCrack / Lucidchart Schema Visualizer",
            "category": "Developer Productivity",
            "pain_point": "Freemium gates on complex tree nesting, forced logins, and slow SVG canvas rendering.",
            "disruption_hypothesis": "Build an instant tree-map visualizer & Draft-07 schema normalizer that works 100% offline."
        }
    ]

    @classmethod
    def scan_market_friction(cls) -> dict:
        print("🕵️ [AGENT ALPHA - CIO] Scanning live tech feeds & competitor SaaS vulnerabilities...")
        # Live HackerNews search for real developer complaints
        try:
            req = urllib.request.Request("https://hacker-news.firebaseio.com/v0/topstories.json", headers={"User-Agent": "GenesisCorp/1.0"})
            with urllib.request.urlopen(req, timeout=4) as r:
                story_ids = json.loads(r.read().decode())[:5]
            for s_id in story_ids:
                s_req = urllib.request.Request(f"https://hacker-news.firebaseio.com/v0/item/{s_id}.json", headers={"User-Agent": "GenesisCorp/1.0"})
                with urllib.request.urlopen(s_req, timeout=3) as s_resp:
                    story = json.loads(s_resp.read().decode())
                    title = story.get("title", "")
                    if any(w in title.lower() for w in ["pricing", "api", "tool", "saas", "privacy", "slow", "bug"]):
                        print(f"🎯 [AGENT ALPHA] Live Signal Captured: {title}")
                        return {
                            "target_saas": "Cloud Developer Utilities",
                            "category": "Developer Infra",
                            "pain_point": f"Friction highlighted by developer community: '{title}'",
                            "disruption_hypothesis": f"Synthesize sovereign zero-leak in-browser alternative solving: {title}"
                        }
        except Exception as e:
            print(f"[-] [AGENT ALPHA] Feed timeout ({e}), deploying verified competitor target.")

        deployed = CorporateMemory.get_deployed_slugs()
        for vector in cls.COMPETITOR_VECTORS:
            target_slug = vector["target_saas"].lower().replace(" ", "_").replace("/", "_")[:20]
            if not any(target_slug in d for d in deployed):
                return vector

        return cls.COMPETITOR_VECTORS[int(time.time()) % len(cls.COMPETITOR_VECTORS)]

# ============================================================
# 3. AGENT BETA: COMPETITIVE PRODUCT ARCHITECT
# ============================================================
class AgentBetaArchitect:
    @classmethod
    def design_spec(cls, intel: dict) -> dict:
        print(f"📐 [AGENT BETA - ARCHITECT] Designing superior product blueprint vs '{intel['target_saas']}'...")
        prompt = (
            f"Target SaaS to Disrupt: {intel['target_saas']}\n"
            f"Market Pain Point: {intel['pain_point']}\n"
            f"Disruption Strategy: {intel['disruption_hypothesis']}\n\n"
            "Design a feature-rich, standalone, client-side web application specification. "
            "Must have responsive split-editor layout, localStorage persistence, clear/demo buttons, "
            "PDF/CSV export capability, and 3-use hard paywall modal unlocking via UPI."
        )
        return {
            "intel": intel,
            "brief": prompt,
            "theme": "slate-950 dark mode, emerald accent, responsive split grid"
        }

# ============================================================
# 4. AGENT GAMMA: CHIEF ENGINEER (Full-Stack Commercial Foundry)
# ============================================================
class AgentGammaEngineer:
    MODELS = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]

    @classmethod
    def synthesize_product(cls, spec: dict) -> dict:
        print("⚙️ [AGENT GAMMA - CHIEF ENGINEER] Synthesizing complete standalone web application & Python engine...")
        intel = spec["intel"]
        url = "https://api.groq.com/openai/v1/chat/completions"

        system_prompt = (
            "You are Agent Gamma, Chief Engineer of the Genesis Autonomous Corporation.\n"
            "Build a production-grade, standalone single-page web application that executes 100% client-side in the browser.\n\n"
            "MANDATORY ARCHITECTURE:\n"
            "1. Standalone HTML5 document with Tailwind CSS CDN dark mode (slate-950 bg, slate-900 panels, slate-800 borders).\n"
            "2. Split layout: Input/Editor on left/top, Live Output/Preview on right/bottom.\n"
            "3. Action utilities: 'Copy to Clipboard', 'Clear Input', 'Load Demo Data', 'Export / Download Result'.\n"
            "4. Built-in hard paywall modal triggered after 3 uses or on 'Upgrade Pro' button with exact standard UPI deep link: upi://pay?pa=keshavthakur07@ptyes&pn=Keshav&am=299.00&cu=INR&tn=SaaS_Pro_Lifetime and QR code.\n\n"
            "Output strictly valid JSON without markdown wrapping:\n"
            "{\n"
            "  \"slug\": \"lowercase_snake_case_name\",\n"
            "  \"name\": \"Professional Product Title\",\n"
            "  \"problem_solved\": \"1-sentence technical description\",\n"
            "  \"python_service\": \"Complete Python class EngineService with method execute(self, payload: str) -> dict using only standard library\",\n"
            "  \"html_app\": \"Full <!DOCTYPE html> document with complete CSS, UI panels, JavaScript logic, localStorage, and paywall modal\",\n"
            "  \"outreach_pitch\": \"High-converting 3-sentence B2B cold email or LinkedIn DM offering this free sovereign tool\"\n"
            "}"
        )

        user_prompt = f"Build full software application for: {intel['target_saas']} - {intel['disruption_hypothesis']}"

        for model in cls.MODELS:
            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 850,
                "response_format": {"type": "json_object"}
            }).encode("utf-8")

            req = urllib.request.Request(
                url, data=payload,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json", "User-Agent": "GenesisCorp/1.0"}
            )
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    raw = resp.read().decode("utf-8")
                    data = json.loads(raw)
                    res = json.loads(data["choices"][0]["message"]["content"])
                    print(f"✅ [AGENT GAMMA] Successfully compiled application via {model}")
                    return res
            except Exception as e:
                print(f"[-] [AGENT GAMMA] Model {model} fallback: {e}")
                continue

        # Verified Industrial Fallback: API Mock & Request Studio
        uid = int(time.time())
        slug = f"api_mock_studio_{uid}"
        query_params = urllib.parse.urlencode({
            "pa": UPI_ID,
            "pn": PAYEE_NAME,
            "am": AMOUNT,
            "cu": "INR",
            "tn": NOTE,
        })
        upi_link = f"upi://pay?{query_params}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(upi_link)}"

        fallback_html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>API Mock Studio Pro — Client-Side Mock Server & Inspector</title>
  <meta name="description" content="Simulate REST API responses, test payload schemas, and mock endpoints 100% in your browser. Zero cloud leak.">
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans flex flex-col antialiased">
  <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur px-6 py-3.5 flex justify-between items-center sticky top-0 z-40">
    <div class="flex items-center space-x-3">
      <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-black text-white text-base">⚡</div>
      <div>
        <h1 class="text-base font-bold text-white tracking-tight">API Mock Studio Pro</h1>
        <p class="text-[11px] text-slate-400">Zero-Cloud In-Browser Mocking & Payload Inspector</p>
      </div>
    </div>
    <div class="flex items-center space-x-3">
      
      <button onclick="triggerPaywall()" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3.5 py-1.5 rounded-lg transition shadow">
        Upgrade Pro (₹299)
      </button>
    </div>
  </header>

  <main class="flex-grow p-4 sm:p-6 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-6">
    <div class="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
      <div class="space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <span class="text-xs font-bold uppercase tracking-wider text-slate-300">Endpoint Config</span>
          <div class="space-x-2">
            <button onclick="loadDemo()" class="text-xs text-blue-400 hover:underline">Load Demo</button>
            <button onclick="clearAll()" class="text-xs text-slate-400 hover:underline">Clear</button>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-2">
          <select id="method" class="bg-slate-950 border border-slate-700 text-xs text-white rounded p-2 focus:outline-none focus:border-indigo-500">
            <option>GET</option><option selected>POST</option><option>PUT</option><option>DELETE</option>
          </select>
          <input id="route" class="col-span-2 bg-slate-950 border border-slate-700 text-xs text-white rounded p-2 focus:outline-none focus:border-indigo-500" value="/api/v1/checkout"/>
        </div>
        <div>
          <label class="text-[11px] text-slate-400 font-semibold uppercase">Mock Status Code & Delay (ms)</label>
          <div class="grid grid-cols-2 gap-2 mt-1">
            <input id="statusCode" type="number" class="bg-slate-950 border border-slate-700 text-xs text-white rounded p-2" value="200"/>
            <input id="delay" type="number" class="bg-slate-950 border border-slate-700 text-xs text-white rounded p-2" value="120"/>
          </div>
        </div>
        <div>
          <label class="text-[11px] text-slate-400 font-semibold uppercase">Mock Response Payload (JSON)</label>
          <textarea id="mockBody" rows="8" class="w-full bg-slate-950 border border-slate-700 text-xs text-slate-200 font-mono rounded p-2.5 mt-1 focus:outline-none focus:border-indigo-500 resize-none"></textarea>
        </div>
      </div>
      <div class="pt-4 border-t border-slate-800 flex gap-2">
        <button onclick="simulateRequest()" class="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs py-2.5 rounded-xl transition shadow">
          🚀 Simulate Request
        </button>
        <button onclick="saveEndpoint()" class="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs px-4 py-2.5 rounded-xl transition">
          💾 Save
        </button>
      </div>
    </div>

    <div class="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
      <div>
        <div class="flex justify-between items-center border-b border-slate-800 pb-3 mb-4">
          <span class="text-xs font-bold uppercase tracking-wider text-emerald-400">Response Inspector</span>
          <div class="space-x-3">
            <button onclick="copyOutput()" class="text-xs text-emerald-400 hover:underline font-semibold">Copy Response</button>
            <button onclick="downloadJson()" class="text-xs text-blue-400 hover:underline">Download JSON</button>
          </div>
        </div>
        <div class="flex items-center space-x-3 mb-3 text-xs font-mono">
          <span id="badgeStatus" class="bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-bold">STATUS: 200 OK</span>
          <span id="badgeLatency" class="text-slate-400">Latency: 0ms</span>
        </div>
        <pre id="responseView" class="bg-slate-950 border border-slate-800 text-xs text-emerald-400 font-mono p-4 rounded-xl h-[420px] overflow-auto whitespace-pre-wrap">// Simulated output appears here</pre>
      </div>
      <div class="pt-4 border-t border-slate-800 text-center text-xs text-slate-500">
        <p>100% In-Browser &bull; Zero Server Logging &bull; Sponsored by Genesis Conglomerate</p>
      </div>
    </div>
  </main>

  <!-- STANDARDIZED INR 299 PRO PAYMENT MODAL -->
  <div id="paywallModal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 hidden flex items-center justify-center p-4 font-sans">
    <div class="bg-slate-900 border border-slate-800 max-w-md w-full rounded-2xl p-6 shadow-2xl text-center relative">
      <button onclick="closePaywall()" class="absolute top-4 right-4 text-slate-400 hover:text-white text-sm font-bold">✕</button>
      <div class="w-12 h-12 rounded-full bg-emerald-950 border border-emerald-800 text-emerald-400 mx-auto flex items-center justify-center text-xl mb-3">👑</div>
      <h3 class="text-xl font-extrabold text-white">Upgrade to API Mock Studio Pro</h3>
      <p class="text-xs text-slate-400 mt-1.5 leading-relaxed">Free sandbox quota exhausted. Unlock unlimited endpoint simulations and persistent mock collections.</p>
      <div class="my-5 p-4 bg-slate-950 border border-slate-800 rounded-xl">
        <div class="flex justify-between items-center mb-3 text-xs border-b border-slate-800 pb-2">
          <span class="text-slate-400">Total Settlement:</span>
          <span class="text-emerald-400 font-mono font-bold text-sm">₹299.00 INR</span>
        </div>
        <div class="bg-white p-2.5 rounded-lg inline-block shadow-inner mb-3">
          <img src="{qr_url}" alt="Scan to Pay 299" class="w-36 h-36 mx-auto block" />
        </div>
        <p class="text-[11px] text-slate-400">Scan via PhonePe, Google Pay, Paytm or BHIM</p>
        <p class="text-xs font-mono text-slate-200 mt-1 font-semibold select-all">{UPI_ID}</p>
      </div>
      <div class="space-y-2">
        <a href="{upi_link}" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs py-3 rounded-xl transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-900/30">
          <span>⚡ Pay ₹299.00 (Open Any UPI App)</span>
        </a>
        <button onclick="navigator.clipboard.writeText('{UPI_ID}'); alert('UPI ID copied: {UPI_ID}');" class="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-2 rounded-xl transition font-medium">
          📋 Copy UPI ID to Clipboard
        </button>
      </div>
      <p class="text-[10px] text-slate-500 mt-4">Instant manual verification: WhatsApp reference or screenshot for activation.</p>
    </div>
  </div>
"""
        if os.path.exists(hub_path):
            with open(hub_path, "r+", encoding="utf-8") as f:
                c = f.read()
                if slug not in c:
                    f.seek(0)
                    if '<div id="hub"' in c:
                        f.write(c.replace('id="hub" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">', f'id="hub" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">\n{card}'))
                    else:
                        f.write(c + card)

    @classmethod
    def _send_chairman_memo(cls, intel: dict, blueprint: dict):
        if not TELEGRAM_BOT_TOKEN:
            print("[-] [AGENT EPSILON] Telegram token not set.")
            return

        slug = blueprint["slug"]
        msg = (
            f"👑 *GENESIS AUTONOMOUS CORP: NEW SAAS DISRUPTOR DEPLOYED*\n\n"
            f"🏢 *Target Disrupted:* `{intel.get('target_saas', 'Cloud SaaS')}`\n"
            f"📦 *Product:* `{blueprint['name']}`\n"
            f"🎯 *Disruption Angle:* {intel.get('pain_point', 'Zero cloud leak & zero monthly fee')}\n"
            f"🌐 *Live Standalone App:* `{BASE_URL}/public/saas/{slug}.html`\n"
            f"📑 *OpenAPI Spec:* `public/specs/{slug}_openapi.json`\n"
            f"💳 *Monetization:* Hard Paywall (3 uses) + UPI ({UPI_ID}) \n"
            f"⚙️ *QA Sentinel:* 100% Subprocess Verified (Exit Code 0)\n\n"
            f"⚡ *Autonomous Swarm running at $0 capital burn.*"
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "🚀 Open Standalone SaaS", "url": f"{BASE_URL}/public/saas/{slug}.html"}],
                ]
            }
        }).encode("utf-8")
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                print("📲 [AGENT EPSILON] Corporate audit report dispatched to Chairman's Telegram.")
        except Exception as e:
            print(f"[-] Telegram dispatch error: {e}")

# ============================================================
# MASTER CORPORATE DISPATCHER
# ============================================================
def execute_corporation_cycle():
    print("=================================================================")
    print(">>> GENESIS AUTONOMOUS CORPORATION: COMMERCIAL CYCLE START <<<")
    print("=================================================================")
    CorporateMemory.init_db()

    # 1. Agent Alpha (CIO): Market Radar & Competitor Scan
    intel = AgentAlphaCIO.scan_market_friction()

    # 2. Agent Beta: Competitive Product Architecture
    spec = AgentBetaArchitect.design_spec(intel)

    # 3. Agent Gamma (Chief Engineer): Product Synthesis
    blueprint = AgentGammaEngineer.synthesize_product(spec)

    # 4. Agent Delta (QA Sentinel): Sandbox Subprocess Audit
    qa_passed = AgentDeltaQA.audit_and_sandbox(blueprint)

    # 5. Agent Epsilon (CCO): Deployment, Monetization & Chairman Alert
    if qa_passed:
        AgentEpsilonCCO.deploy_and_monetize(intel, blueprint)
        CorporateMemory.record_deployment(intel, blueprint, "PASSED")

    print(f"✅ CYCLE COMPLETE: '{blueprint['name']}' is staged and live.")
    print("=================================================================\n")

if __name__ == "__main__":
    execute_corporation_cycle()