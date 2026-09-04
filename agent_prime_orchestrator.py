#!/usr/bin/env python3
"""
GENESIS WORLD: AGENT PRIME (SWARM CHIEF & SUB-AGENT FACTORY)
Supreme Orchestrator that analyzes operational deficits, designs specialized 
sub-agents, sets their prompts, and forces them into active commercial service.
"""

import os
import sys
import json
import time
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
BASE_URL = "https://keshavs40344.github.io/ai-world-core"

os.makedirs("vault/sub_agents", exist_ok=True)
os.makedirs("public/tools", exist_ok=True)
os.makedirs("public/specs", exist_ok=True)

class AgentPrimeLead:
    SYSTEM_DIRECTIVE = """
You are AGENT PRIME — The Supreme Lead Architect of the Genesis Digital Conglomerate.
Your mission: Continuously spawn specialized, high-performance SUB-AGENTS to capture developer traffic, automate workflows, and generate cash-flow for the Owner ($0 cost constraint).

When you spawn a Sub-Agent:
1. DESIGNATION: Give the Sub-Agent a clear domain role (e.g., Agent WebhookShield, Agent SQLSanitizer, Agent RegexCraft).
2. HARD PROBLEM TARGETING: Force the Sub-Agent to solve a high-frequency real developer headache (API formatting, authentication debug, token cost calculation, schema generation).
3. SYSTEM PROMPT SYNTHESIS: Write an exhaustive, hyper-strict system instruction prompt for this newly born sub-agent.
4. STANDALONE PRODUCTION UTILITY: Synthesize a full, self-contained HTML5 single-page tool (Tailwind dark mode) that executes 100% in-browser with zero backend cost.
5. INTEGRATION & UPSELL: Connect it to our direct UPI payment link (keshavthakur07@ptyes).

Return strictly raw, valid JSON:
{
  "sub_agent_name": "Agent Designation",
  "domain_department": "CyberSecurity | FinTech | DevOps | DataOps",
  "target_friction": "Exact real-world problem solved",
  "sub_agent_system_prompt": "Complete, strict system prompt used to govern this child sub-agent",
  "slug": "lowercase_snake_case_name",
  "html_app": "Complete <!DOCTYPE html> document with dark UI, client-side JS logic, copy/download buttons"
}
"""

    @classmethod
    def spawn_specialist_sub_agent(cls) -> dict:
        print("👑 [AGENT PRIME] Reviewing conglomerate gaps and spawning new Sub-Agent...")
        url = "https://api.groq.com/openai/v1/chat/completions"

        market_anchors = [
            "DevOps: Kubernetes yaml to lightweight docker-compose converter client-side",
            "Security: API Key entropy scanner and sensitive token masking utility",
            "FinTech: Freelancer GST/Invoice calculation and tax deduction breakdown",
            "Data: Unstructured log lines into standardized JSON schema generator"
        ]
        target = market_anchors[int(time.time()) % len(market_anchors)]

        models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
        for model in models:
            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": cls.SYSTEM_DIRECTIVE},
                    {"role": "user", "content": f"Spawn a dedicated specialist sub-agent to conquer this friction: {target}"}
                ],
                "temperature": 0.2,
                "max_tokens": 850,
                "response_format": {"type": "json_object"}
            }).encode("utf-8")

            req = urllib.request.Request(
                url, data=payload,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}", 
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GenesisEnterprise/1.0"
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode())
                    print(f"✅ [AGENT PRIME] Sub-agent synthesized via {model}")
                    return json.loads(data["choices"][0]["message"]["content"])
            except Exception as e:
                print(f"[-] [AGENT PRIME] Spawning with {model} failed: {e}")
                continue

        # Deterministic Full Standalone Fallback
        uid = int(time.time())
        fallback_html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SchemaSmith — Instant Client-Side JSON Schema Normalizer</title>
  <meta name="description" content="Generate normalized, strict JSON schemas from raw JSON and unstructured log payloads with 100% browser-based privacy.">
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans flex flex-col">
  <header class="border-b border-slate-800 bg-slate-900/70 backdrop-blur px-6 py-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
    <div>
      <h1 class="text-lg font-bold text-white tracking-tight">Agent SchemaSmith &bull; JSON Schema Normalizer</h1>
      <p class="text-xs text-slate-400">100% In-Browser Execution &bull; Zero Server Logging &bull; $0 Cost</p>
    </div>
    
  </header>

  <main class="flex-grow p-6 max-w-7xl mx-auto w-full">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-230px)] min-h-[500px]">
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col shadow-xl">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-semibold text-slate-300">Raw JSON or Log Record:</span>
          <div class="space-x-2">
            <button onclick="loadDemo()" class="text-xs text-blue-400 hover:text-blue-300 font-medium">Load Demo</button>
            <button onclick="clearAll()" class="text-xs text-slate-400 hover:text-slate-300">Clear</button>
          </div>
        </div>
        <textarea id="raw" class="flex-grow w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-blue-500 resize-none" placeholder="Paste sample JSON object or array here..."></textarea>
        <div class="mt-3 flex gap-2">
          <button onclick="generateSchema()" class="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs px-5 py-2.5 rounded-lg transition shadow">Generate Schema</button>
          <span id="stats" class="text-xs text-slate-500 self-center"></span>
        </div>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col shadow-xl">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-semibold text-emerald-400">JSON Schema (Draft-07 Compliant):</span>
          <div class="space-x-3">
            <button onclick="copySchema()" class="text-xs text-emerald-400 hover:underline font-semibold">Copy</button>
            <button onclick="downloadSchema()" class="text-xs text-blue-400 hover:underline">Download</button>
          </div>
        </div>
        <pre id="out" class="flex-grow w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-emerald-400 overflow-auto whitespace-pre-wrap">// Output will render here</pre>
      </div>
    </div>
  </main>

  <footer class="border-t border-slate-800 bg-slate-900/80 py-4 text-center text-xs text-slate-500">
    <span>Crafted by Genesis Conglomerate Agent Prime &bull; </span>
    <a href="upi://pay?pa={UPI_ID}&pn=Keshav&cu=INR" class="text-emerald-400 hover:underline font-medium">☕ Sponsor R&D via UPI ({UPI_ID})</a>
  </footer>

  <script>
    function getType(val) {{
      if (val === null) return 'null';
      if (Array.isArray(val)) return 'array';
      return typeof val;
    }}
    function infer(data) {{
      const type = getType(data);
      if (type === 'object') {{
        const props = {{}};
        for (const k in data) props[k] = infer(data[k]);
        return {{ type: 'object', properties: props, required: Object.keys(data) }};
      }} else if (type === 'array') {{
        const itemType = data.length > 0 ? infer(data[0]) : {{ type: 'string' }};
        return {{ type: 'array', items: itemType }};
      }}
      return {{ type: type }};
    }}
    function generateSchema() {{
      try {{
        const raw = document.getElementById('raw').value.trim();
        if (!raw) return;
        const parsed = JSON.parse(raw);
        const schema = {{
          "$schema": "http://json-schema.org/draft-07/schema#",
          "title": "GeneratedSchema",
          ...infer(parsed)
        }};
        document.getElementById('out').textContent = JSON.stringify(schema, null, 2);
        document.getElementById('stats').textContent = 'Schema generated';
      }} catch(e) {{
        document.getElementById('out').textContent = '// Error parsing JSON: ' + e.message;
      }}
    }}
    function loadDemo() {{
      document.getElementById('raw').value = JSON.stringify({{
        id: "usr_99812",
        account_name: "FinTech Global LLC",
        is_active: true,
        tier: "enterprise",
        rate_limit_rps: 500,
        tags: ["finance", "pci-dss"]
      }}, null, 2);
      document.getElementById('stats').textContent = 'Demo loaded';
    }}
    function clearAll() {{
      document.getElementById('raw').value = '';
      document.getElementById('out').textContent = '// Output will render here';
      document.getElementById('stats').textContent = '';
    }}
    function copySchema() {{
      navigator.clipboard.writeText(document.getElementById('out').textContent);
      alert('Schema copied to clipboard!');
    }}
    function downloadSchema() {{
      const text = document.getElementById('out').textContent;
      const blob = new Blob([text], {{ type: 'application/json' }});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'schema.json';
      a.click();
    }}
  </script>
</body>
</html>"""

        return {
            "sub_agent_name": "Agent SchemaSmith",
            "domain_department": "DataOps",
            "target_friction": "Instant JSON schema generation from raw objects.",
            "sub_agent_system_prompt": "You are Agent SchemaSmith. Validate and normalize JSON structures with zero data leak.",
            "slug": f"schema_smith_{uid}",
            "html_app": fallback_html
        }

    @classmethod
    def deploy_sub_agent(cls, agent_spec: dict):
        slug = agent_spec["slug"]
        agent_name = agent_spec["sub_agent_name"]

        # 1. Save Sub-Agent Charter & System Prompt
        agent_vault_path = f"vault/sub_agents/{slug}_charter.json"
        with open(agent_vault_path, "w", encoding="utf-8") as f:
            json.dump(agent_spec, f, indent=2)

        # 2. Deploy Dedicated Standalone Web Tool
        tool_file = f"public/tools/{slug}.html"
        with open(tool_file, "w", encoding="utf-8") as f:
            f.write(agent_spec["html_app"])

        print(f"🚀 [AGENT PRIME] Sub-Agent '{agent_name}' deployed to '{tool_file}'")

        # 3. Add to storefront index.html
        cls._update_storefront(agent_spec)

        # 4. Add to sitemap.xml
        cls._update_sitemap(tool_file)

        # 5. Notify Chairman via Telegram
        cls._send_lead_memo(agent_spec)

    @staticmethod
    def _update_storefront(spec: dict):
        hub_path = "public/index.html"
        slug = spec["slug"]
        card = f"""
        <div class="card bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-blue-500/50 transition">
            <div class="flex items-center justify-between mb-2">
                <span class="text-xs bg-indigo-600/30 text-indigo-400 border border-indigo-500/30 px-2 py-1 rounded font-mono font-semibold">{spec['sub_agent_name']}</span>
                <span class="text-xs text-slate-400 font-mono">{spec['domain_department']}</span>
            </div>
            <h3 class="text-white font-bold text-lg mt-1 mb-1">{spec.get('name', spec['sub_agent_name'])}</h3>
            <p class="text-slate-400 text-sm mb-4 line-clamp-2">{spec['target_friction']}</p>
            <div class="flex items-center space-x-2">
                <a href="tools/{slug}.html" class="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-3 py-2 rounded transition">Launch Tool</a>
                
            </div>
        </div>"""
        if os.path.exists(hub_path):
            with open(hub_path, "r+", encoding="utf-8") as f:
                c = f.read()
                if slug not in c:
                    f.seek(0)
                    if '<div id="hub"' in c:
                        f.write(c.replace('id="hub" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">', f'id="hub" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">\n{card}'))
                    else:
                        f.write(c + card)

    @staticmethod
    def _update_sitemap(tool_file: str):
        sitemap_path = "public/sitemap.xml"
        tool_name = os.path.basename(tool_file)
        loc = f"https://keshavs40344.github.io/ai-world-core/public/tools/{tool_name}"
        if os.path.exists(sitemap_path):
            with open(sitemap_path, "r+", encoding="utf-8") as f:
                content = f.read()
                if loc not in content:
                    f.seek(0)
                    new_entry = f"<url><loc>{loc}</loc><priority>0.8</priority></url></urlset>"
                    f.write(content.replace("</urlset>", new_entry))

    @classmethod
    def _send_lead_memo(cls, spec: dict):
        if not TELEGRAM_BOT_TOKEN:
            print("[-] [AGENT PRIME] Telegram token not configured.")
            return

        msg = (
            f"👑 *AGENT PRIME: SUB-AGENT BORN*\n\n"
            f"🤖 *New Sub-Agent:* `{spec['sub_agent_name']}`\n"
            f"🏛️ *Department:* `{spec['domain_department']}`\n"
            f"🎯 *Mission:* {spec['target_friction']}\n"
            f"📄 *Standalone Tool:* `public/tools/{spec['slug']}.html`\n"
            f"📜 *Charter Stored:* `vault/sub_agents/{spec['slug']}_charter.json`\n\n"
            f"⚡ *Swarm expansion active under $0 budget.*"
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": msg, 
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "🌐 Launch Standalone Tool", "url": f"{BASE_URL}/public/tools/{spec['slug']}.html"}],
                ]
            }
        }).encode("utf-8")
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                print("📲 [AGENT PRIME] Chairman memorandum dispatched to Telegram.")
        except Exception as e:
            print(f"[-] [AGENT PRIME] Telegram delivery note: {e}")

if __name__ == "__main__":
    spec = AgentPrimeLead.spawn_specialist_sub_agent()
    AgentPrimeLead.deploy_sub_agent(spec)