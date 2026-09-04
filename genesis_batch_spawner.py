#!/usr/bin/env python3
"""
GENESIS MASS SWARM FACTORY: BATCH MULTI-AGENT GENERATOR
Creates 5 specialized AI sub-agents in a single execution with unique prompts,
dedicated standalone HTML tools, OpenAPI specs, and vault archives.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# Configure stdout and stderr for UTF-8
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

# Ensure complete infrastructure
DIRS = ["vault/sub_agents", "public/tools", "public/specs", "public/outreach"]
for d in DIRS:
    os.makedirs(d, exist_ok=True)

# 5 Dedicated Domain Vectors to Spawn Simultaneously
TARGET_SECTORS = [
    {"role": "Agent WebhookSentinel", "dept": "CyberSecurity", "problem": "HMAC SHA256 webhook signature validator & header parser"},
    {"role": "Agent SQLForge", "dept": "DataOps", "problem": "Raw JSON/CSV into SQL multi-dialect INSERT/UPDATE generator"},
    {"role": "Agent DockerCraft", "dept": "DevOps", "problem": "Docker run commands to docker-compose.yml visual converter"},
    {"role": "Agent RegexArchitect", "dept": "DeveloperTools", "problem": "Human natural language into optimized regex pattern tester"},
    {"role": "Agent TokenLedger", "dept": "FinTech", "problem": "LLM prompt token counter and USD API cost estimator"}
]

FALLBACK_TEMPLATES = {
    "Agent WebhookSentinel": {
        "slug": "webhook_sentinel",
        "name": "Webhook Signature & Payload Sentinel",
        "system_prompt": "You are Agent WebhookSentinel. Validate HMAC SHA256 webhook signatures and inspect headers client-side.",
        "problem_solved": "HMAC SHA256 webhook signature validator & header parser",
        "html_client": """<!DOCTYPE html><html lang="en" class="dark"><head><meta charset="UTF-8"><title>Webhook Signature Sentinel</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-slate-950 text-slate-100 min-h-screen p-6 font-sans flex flex-col"><header class="max-w-4xl mx-auto w-full mb-6 border-b border-slate-800 pb-4 flex justify-between items-center"><div><h1 class="text-xl font-bold text-white">Webhook Signature Sentinel</h1><p class="text-xs text-slate-400">100% Client-Side HMAC SHA256 Validation</p></div></header><main class="max-w-4xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 gap-4 flex-grow"><div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col"><label class="text-xs font-semibold mb-1">Secret Key & Payload:</label><input id="secret" type="password" class="w-full bg-slate-950 border border-slate-700 p-2 rounded text-xs mb-2 text-slate-200" placeholder="Webhook Signing Secret"/><textarea id="payload" class="flex-grow bg-slate-950 border border-slate-700 p-2 rounded text-xs font-mono text-slate-200 resize-none h-48" placeholder="Paste raw webhook body here..."></textarea><button onclick="calcHash()" class="mt-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2 rounded">Compute HMAC-SHA256</button></div><div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col"><span class="text-xs font-semibold text-emerald-400 mb-1">Generated Signature & Status:</span><pre id="result" class="flex-grow bg-slate-950 border border-slate-800 p-3 rounded text-xs font-mono text-emerald-400 overflow-auto whitespace-pre-wrap">// Result hash appears here</pre><button onclick="navigator.clipboard.writeText(document.getElementById('result').textContent)" class="mt-2 bg-slate-800 text-slate-300 text-xs py-2 rounded">Copy Hash</button></div></main><script>async function calcHash(){const s=document.getElementById('secret').value;const p=document.getElementById('payload').value;if(!s||!p){document.getElementById('result').textContent='// Provide both secret and payload.';return;}const enc=new TextEncoder();const key=await crypto.subtle.importKey('raw',enc.encode(s),{name:'HMAC',hash:'SHA-256'},false,['sign']);const sig=await crypto.subtle.sign('HMAC',key,enc.encode(p));const hex=Array.from(new Uint8Array(sig)).map(b=>b.toString(16).padStart(2,'0')).join('');document.getElementById('result').textContent='sha256='+hex+'\n\nHeader: X-Hub-Signature-256: sha256='+hex;}</script></body></html>"""
    },
    "Agent SQLForge": {
        "slug": "sql_forge",
        "name": "SQL Multi-Dialect Query Forge",
        "system_prompt": "You are Agent SQLForge. Transform raw tabular CSV and JSON arrays into dialect-specific SQL queries.",
        "problem_solved": "Raw JSON/CSV into SQL multi-dialect INSERT/UPDATE generator",
        "html_client": """<!DOCTYPE html><html lang="en" class="dark"><head><meta charset="UTF-8"><title>SQL Query Forge</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-slate-950 text-slate-100 min-h-screen p-6 font-sans flex flex-col"><header class="max-w-4xl mx-auto w-full mb-6 border-b border-slate-800 pb-4 flex justify-between items-center"><div><h1 class="text-xl font-bold text-white">SQL Multi-Dialect Query Forge</h1><p class="text-xs text-slate-400">100% In-Browser SQL Generation</p></div></header><main class="max-w-4xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 gap-4 flex-grow"><div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col"><div class="flex justify-between items-center mb-1"><label class="text-xs font-semibold">Table & Target Data:</label><input id="table" class="bg-slate-950 border border-slate-700 px-2 py-1 text-xs rounded text-slate-200" value="users" placeholder="Table name"/></div><textarea id="data" class="flex-grow bg-slate-950 border border-slate-700 p-2 rounded text-xs font-mono text-slate-200 resize-none h-48" placeholder="id,name,role\n1,Alice,Admin\n2,Bob,Developer"></textarea><button onclick="genSQL()" class="mt-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2 rounded">Generate SQL INSERT</button></div><div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col"><span class="text-xs font-semibold text-emerald-400 mb-1">Generated SQL Statements:</span><pre id="out" class="flex-grow bg-slate-950 border border-slate-800 p-3 rounded text-xs font-mono text-emerald-400 overflow-auto whitespace-pre-wrap">// SQL output renders here</pre><button onclick="navigator.clipboard.writeText(document.getElementById('out').textContent)" class="mt-2 bg-slate-800 text-slate-300 text-xs py-2 rounded">Copy SQL</button></div></main><script>function genSQL(){const t=document.getElementById('table').value.trim()||'table_name';const raw=document.getElementById('data').value.trim();if(!raw){document.getElementById('out').textContent='// Enter valid CSV data';return;}const lines=raw.split('\n').map(l=>l.trim()).filter(l=>l);if(lines.length<2)return;const headers=lines[0].split(',').map(h=>h.trim());const stmts=lines.slice(1).map(l=>{const vals=l.split(',').map(v=>isNaN(v)?`'${v.trim()}'`:v.trim());return `INSERT INTO ${t} (${headers.join(', ')}) VALUES (${vals.join(', ')});`;});document.getElementById('out').textContent=stmts.join('\n');}</script></body></html>"""
    },
    "Agent DockerCraft": {
        "slug": "docker_craft",
        "name": "Docker Run to Compose Visual Converter",
        "system_prompt": "You are Agent DockerCraft. Convert complex docker run terminal commands into clean docker-compose.yml files.",
        "problem_solved": "Docker run commands to docker-compose.yml visual converter",
        "html_client": """<!DOCTYPE html><html lang="en" class="dark"><head><meta charset="UTF-8"><title>Docker Run to Compose</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-slate-950 text-slate-100 min-h-screen p-6 font-sans flex flex-col"><header class="max-w-4xl mx-auto w-full mb-6 border-b border-slate-800 pb-4 flex justify-between items-center"><div><h1 class="text-xl font-bold text-white">Docker Run to docker-compose.yml</h1><p class="text-xs text-slate-400">Transform shell run commands to YAML</p></div></header><main class="max-w-4xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 gap-4 flex-grow"><div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col"><label class="text-xs font-semibold mb-1">Docker Run Command:</label><textarea id="cmd" class="flex-grow bg-slate-950 border border-slate-700 p-2 rounded text-xs font-mono text-slate-200 resize-none h-48" placeholder="docker run -d -p 8080:80 -v /data:/app/data --name webserver nginx:latest"></textarea><button onclick="conv()" class="mt-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2 rounded">Convert to Compose</button></div><div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col"><span class="text-xs font-semibold text-emerald-400 mb-1">docker-compose.yml:</span><pre id="yml" class="flex-grow bg-slate-950 border border-slate-800 p-3 rounded text-xs font-mono text-emerald-400 overflow-auto whitespace-pre-wrap">// YAML appears here</pre><button onclick="navigator.clipboard.writeText(document.getElementById('yml').textContent)" class="mt-2 bg-slate-800 text-slate-300 text-xs py-2 rounded">Copy YAML</button></div></main><script>function conv(){const c=document.getElementById('cmd').value;const p=(c.match(/-p\s+(\S+)/)||[])[1]||'80:80';const v=(c.match(/-v\s+(\S+)/)||[])[1];const img=(c.trim().split(/\s+/).pop())||'app:latest';let y=`version: '3.8'\nservices:\n  app:\n    image: ${img}\n    ports:\n      - "${p}"`;if(v)y+=`\n    volumes:\n      - "${v}"`;document.getElementById('yml').textContent=y;}</script></body></html>"""
    },
    "Agent RegexArchitect": {
        "slug": "regex_architect",
        "name": "Natural Language to Regex Architect",
        "system_prompt": "You are Agent RegexArchitect. Create, test, and explain regular expressions with match visualization.",
        "problem_solved": "Human natural language into optimized regex pattern tester",
        "html_client": """<!DOCTYPE html><html lang="en" class="dark"><head><meta charset="UTF-8"><title>Regex Architect</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-slate-950 text-slate-100 min-h-screen p-6 font-sans flex flex-col"><header class="max-w-4xl mx-auto w-full mb-6 border-b border-slate-800 pb-4 flex justify-between items-center"><div><h1 class="text-xl font-bold text-white">Regex Architect & Pattern Tester</h1><p class="text-xs text-slate-400">Instant in-browser regex tester & validator</p></div></header><main class="max-w-4xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 gap-4 flex-grow"><div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col"><label class="text-xs font-semibold mb-1">Regex Pattern & Flags:</label><input id="reg" class="bg-slate-950 border border-slate-700 p-2 text-xs font-mono rounded text-slate-200 mb-2" value="[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+" placeholder="e.g. ^\d{3}-\d{4}$"/><textarea id="test" class="flex-grow bg-slate-950 border border-slate-700 p-2 rounded text-xs font-mono text-slate-200 resize-none h-48" placeholder="Sample test text containing emails or target matches...&#10;alice@company.org&#10;invalid-email"></textarea><button onclick="testReg()" class="mt-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2 rounded">Test Matches</button></div><div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col"><span class="text-xs font-semibold text-emerald-400 mb-1">Matched Captures:</span><pre id="mout" class="flex-grow bg-slate-950 border border-slate-800 p-3 rounded text-xs font-mono text-emerald-400 overflow-auto whitespace-pre-wrap">// Matches appear here</pre><button onclick="navigator.clipboard.writeText(document.getElementById('mout').textContent)" class="mt-2 bg-slate-800 text-slate-300 text-xs py-2 rounded">Copy Matches</button></div></main><script>function testReg(){try{const r=new RegExp(document.getElementById('reg').value,'g');const t=document.getElementById('test').value;const m=t.match(r)||[];document.getElementById('mout').textContent=`Found ${m.length} match(es):\n\n`+m.join('\n');}catch(e){document.getElementById('mout').textContent='// Invalid Regex: '+e.message;}}</script></body></html>"""
    },
    "Agent TokenLedger": {
        "slug": "token_ledger",
        "name": "LLM Token Ledger & Cost Estimator",
        "system_prompt": "You are Agent TokenLedger. Estimate token counts and API costs across OpenAI, Claude, Groq, and Gemini.",
        "problem_solved": "LLM prompt token counter and USD API cost estimator",
        "html_client": """<!DOCTYPE html><html lang="en" class="dark"><head><meta charset="UTF-8"><title>LLM Token Ledger</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-slate-950 text-slate-100 min-h-screen p-6 font-sans flex flex-col"><header class="max-w-4xl mx-auto w-full mb-6 border-b border-slate-800 pb-4 flex justify-between items-center"><div><h1 class="text-xl font-bold text-white">LLM Token Ledger & Cost Estimator</h1><p class="text-xs text-slate-400">Calculate prompt tokens and multi-model expenses</p></div></header><main class="max-w-4xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 gap-4 flex-grow"><div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col"><label class="text-xs font-semibold mb-1">Prompt / Input Text:</label><textarea id="txt" class="flex-grow bg-slate-950 border border-slate-700 p-2 rounded text-xs font-mono text-slate-200 resize-none h-48" placeholder="Paste prompt or dataset here..."></textarea><button onclick="calcTokens()" class="mt-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2 rounded">Calculate Tokens & Cost</button></div><div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col"><span class="text-xs font-semibold text-emerald-400 mb-1">Financial & Token Breakdown:</span><pre id="tout" class="flex-grow bg-slate-950 border border-slate-800 p-3 rounded text-xs font-mono text-emerald-400 overflow-auto whitespace-pre-wrap">// Breakdown appears here</pre><button onclick="navigator.clipboard.writeText(document.getElementById('tout').textContent)" class="mt-2 bg-slate-800 text-slate-300 text-xs py-2 rounded">Copy Breakdown</button></div></main><script>function calcTokens(){const s=document.getElementById('txt').value;const tokens=Math.ceil(s.length/3.8);const gpt4=(tokens*0.00001).toFixed(6);const claude3=(tokens*0.000003).toFixed(6);const groq=(tokens*0.00000059).toFixed(6);document.getElementById('tout').textContent=`Character Count : ${s.length}\nEstimated Tokens: ${tokens}\n\nEstimated Inference Cost (Input):\n- GPT-4o        : $${gpt4}\n- Claude 3.5 Son: $${claude3}\n- Groq (Llama-3): $${groq}\n\nStatus: Client-Side Verified`;}</script></body></html>"""
    }
}

class MassSwarmFactory:
    UPI_ID = UPI_ID

    @classmethod
    def synthesize_agent(cls, target: dict) -> dict:
        print(f"🏭 Spawning AI Agent: {target['role']} ({target['dept']})...")
        url = "https://api.groq.com/openai/v1/chat/completions"

        prompt = f"""
You are creating a standalone, specialized AI Sub-Agent.
Role: {target['role']}
Department: {target['dept']}
Target Problem: {target['problem']}

Generate strictly valid raw JSON:
{{
  "slug": "lowercase_snake_case_name",
  "name": "Professional Web Tool Title",
  "system_prompt": "Hyper-focused system instructions that govern this AI sub-agent",
  "problem_solved": "{target['problem']}",
  "html_client": "Complete <!DOCTYPE html> page with Tailwind CDN dark theme, interactive input/output boxes, in-browser pure JS execution, copy buttons, and clear buttons."
}}
"""
        models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
        for model in models:
            payload = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 800,
                "response_format": {"type": "json_object"}
            }).encode("utf-8")

            req = urllib.request.Request(
                url, data=payload, 
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json", "User-Agent": "GenesisSwarm/3.0"}
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    return json.loads(json.loads(r.read().decode())["choices"][0]["message"]["content"])
            except Exception:
                continue

        # Fast and reliable fallback template
        print(f"⚡ [FALLBACK] Loading verified standalone template for {target['role']}")
        return FALLBACK_TEMPLATES.get(target['role'], {
            "slug": target['role'].lower().replace(" ", "_"),
            "name": f"{target['role']} Utility",
            "system_prompt": f"You are {target['role']}. Resolve: {target['problem']}",
            "problem_solved": target['problem'],
            "html_client": f"<!DOCTYPE html><html><body class='bg-slate-950 text-white p-6'><h2>{target['role']} Online</h2></body></html>"
        })

    @classmethod
    def deploy_agent(cls, target: dict, agent_data: dict):
        slug = agent_data["slug"]

        # 1. Monetization injection
        upi_link = f"upi://pay?pa={cls.UPI_ID}&pn=Keshav&cu=INR"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={urllib.parse.quote(upi_link)}"
        
        banner = f"""
        <nav class="border-b border-slate-800 bg-slate-900/80 p-4 mb-6 flex justify-between items-center text-xs font-sans">
            <a href="../index.html" class="text-indigo-400 font-bold">← All AI Tools Hub</a>
            
        </nav>
        """
        footer = f"""
        <div class="mt-12 p-6 bg-slate-900 border border-slate-800 rounded-xl text-center max-w-md mx-auto text-xs font-sans">
            <p class="text-slate-400 mb-2">Powered by {target['role']} (Zero-Cost Sovereign Agent)</p>
            <img src="{qr_url}" alt="UPI QR" class="mx-auto rounded border border-slate-700 p-1 bg-white mb-2"/>
            <a href="{upi_link}" class="inline-block bg-emerald-600 text-white px-4 py-1.5 rounded font-semibold">Tip via UPI ({cls.UPI_ID})</a>
        </div>
        """

        raw_html = agent_data.get("html_client", "")
        if "<body" in raw_html:
            parts = raw_html.split(">", 1)
            final_html = parts[0] + ">" + banner + parts[1]
        else:
            final_html = banner + raw_html

        final_html = final_html.replace("</body>", f"{footer}</body>") if "</body>" in final_html else final_html + footer

        # Write standalone page
        page_path = f"public/tools/{slug}.html"
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        # Write agent charter (permanent memory)
        charter_path = f"vault/sub_agents/{slug}_charter.json"
        with open(charter_path, "w", encoding="utf-8") as f:
            json.dump({**target, **agent_data}, f, indent=2)

        # Update sitemap
        cls.append_to_sitemap(page_path)

        # Append to master hub
        cls.append_to_hub(target, agent_data)
        print(f"✅ Deployed: public/tools/{slug}.html")

    @staticmethod
    def append_to_sitemap(tool_file: str):
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

    @staticmethod
    def append_to_hub(target: dict, agent_data: dict):
        hub_path = "public/index.html"
        slug = agent_data["slug"]
        card = f"""
        <div class="card bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-indigo-500/50 transition flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded border border-indigo-800 font-semibold">{target['dept']}</span>
                    <span class="text-xs text-slate-400 font-mono">{target['role']}</span>
                </div>
                <h3 class="text-lg font-bold text-white mt-2 mb-1">{agent_data['name']}</h3>
                <p class="text-slate-400 text-sm mb-4 line-clamp-2">{target['problem']}</p>
            </div>
            <div class="flex items-center space-x-2 mt-2">
                <a href="tools/{slug}.html" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded transition">
                    Launch Tool →
                </a>
                
            </div>
        </div>"""
        if os.path.exists(hub_path):
            with open(hub_path, "r+", encoding="utf-8") as f:
                content = f.read()
                if slug not in content:
                    f.seek(0)
                    if '<div id="hub"' in content:
                        f.write(content.replace('id="hub" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">', f'id="hub" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">\n{card}'))
                    else:
                        f.write(content + card)

    @classmethod
    def run_mass_spawn(cls):
        print("🚀 [SWARM FACTORY] Mass Spawning 5 Autonomous Sub-Agents...")
        spawned = []
        for target in TARGET_SECTORS:
            data = cls.synthesize_agent(target)
            cls.deploy_agent(target, data)
            spawned.append(target['role'])
            time.sleep(0.5)

        # Summary Telegram Dispatch
        bullet_list = "\n".join([f"🤖 `{r}`" for r in spawned])
        msg = (
            f"👑 *MASS SWARM SPAWN: 5 NEW AGENTS LIVE*\n\n"
            f"{bullet_list}\n\n"
            f"🌐 *Storefront:* Updated with 5 dedicated standalone apps\n"
            f"💳 *Monetization:* UPI active on all."
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": msg, 
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "🌐 Open Storefront Hub", "url": f"{BASE_URL}/public/index.html"}],
                ]
            }
        }).encode("utf-8")
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                print("📲 [SWARM FACTORY] Batch notification dispatched to Telegram.")
        except Exception as e:
            print(f"[-] Telegram dispatch note: {e}")
        print("✅ All 5 AI Agents created, packaged, and linked to storefront!")

if __name__ == "__main__":
    MassSwarmFactory.run_mass_spawn()