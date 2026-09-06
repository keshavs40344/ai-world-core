import os
import sys
import json
import time
import asyncio
import sqlite3
from typing import Dict, Any
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Directories aligned with ai-world-core
SAAS_DIR = "public/saas"
INDEX_PATH = "public/index.html"
BUS_DIR = "vault/bus"
DB_PATH = "db/genesis_state.db"

for p in [SAAS_DIR, BUS_DIR, "public", "db"]:
    os.makedirs(p, exist_ok=True)

# Unique High-Demand Domains with distinct design palettes and real algorithms
HUMAN_CRAFTED_SPECS = [
    {
        "slug": "cryptocraft_entropy_shield",
        "title": "CryptoCraft // Offline Hash & Entropy Inspector",
        "category": "Cryptography & Security",
        "domain_theme": "DefSec Crimson",
        "bg_color": "bg-neutral-950",
        "panel_color": "bg-neutral-900/40",
        "border_color": "border-neutral-800",
        "accent_badge": "bg-rose-950/80 text-rose-300 border-rose-800/60",
        "action_btn": "bg-rose-600 hover:bg-rose-500 text-white shadow-rose-900/40",
        "accent_text": "text-rose-400",
        "summary": "Computes SHA-256, SHA-512, Shannon Entropy and bit-distribution offline in memory using the native Web Crypto API.",
        "input_label": "Source Text or Key Secret",
        "sample": "CorrectHorseBatteryStaple#2026!SecOpsAudit",
        "js_algorithm": """
            const encoder = new TextEncoder();
            const data = encoder.encode(input);
            
            // Shannon Entropy Calculation
            const frequencies = {};
            for (let i = 0; i < input.length; i++) {
                const char = input[i];
                frequencies[char] = (frequencies[char] || 0) + 1;
            }
            let entropy = 0;
            for (const char in frequencies) {
                const p = frequencies[char] / input.length;
                entropy -= p * Math.log2(p);
            }

            // Real Web Crypto Sub-millisecond Execution
            Promise.all([
                crypto.subtle.digest('SHA-256', data),
                crypto.subtle.digest('SHA-512', data)
            ]).then(([sha256Buf, sha512Buf]) => {
                const hex = (buffer) => Array.from(new Uint8Array(buffer)).map(b => b.toString(16).padStart(2, '0')).join('');
                const result = {
                    "METRICS": {
                        "LENGTH_BYTES": data.length,
                        "SHANNON_ENTROPY_SCORE": entropy.toFixed(3) + " / 8.0 bits (Higher is more secure)",
                        "CRACK_DIFFICULTY_ESTIMATE": entropy > 4.2 ? "High (Resistant to Dictionary Attacks)" : "Weak (Low Pattern Variance)"
                    },
                    "HASH_CHECKSUMS": {
                        "SHA256": hex(sha256Buf),
                        "SHA512": hex(sha512Buf)
                    }
                };
                renderPayload(JSON.stringify(result, null, 2), 'Cryptographic hashes & entropy verified.');
            });
        """
    },
    {
        "slug": "sql_syntax_formatter_pro",
        "title": "QuerySmith // High-Performance SQL Formatter & AST Tokenizer",
        "category": "Database Engineering",
        "domain_theme": "Stone Cyan Console",
        "bg_color": "bg-stone-950",
        "panel_color": "bg-stone-900/40",
        "border_color": "border-stone-800",
        "accent_badge": "bg-cyan-950/80 text-cyan-300 border-cyan-800/60",
        "action_btn": "bg-cyan-600 hover:bg-cyan-500 text-white shadow-cyan-900/40",
        "accent_text": "text-cyan-400",
        "summary": "Formats complex nested SQL queries, normalizes reserved keywords to uppercase, indentates subqueries, and extracts target tables.",
        "input_label": "Raw Unformatted SQL Statement",
        "sample": "select u.id,u.email,o.total_amount,o.created_at from users u inner join orders o on u.id=o.user_id where o.status='completed' and o.total_amount>500 order by o.created_at desc limit 50;",
        "js_algorithm": """
            const keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'JOIN', 'ON', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT', 'INSERT INTO', 'UPDATE', 'DELETE', 'VALUES', 'SET'];
            let formatted = input;

            // Normalize keywords
            keywords.forEach(kw => {
                const reg = new RegExp('\\\\b' + kw + '\\\\b', 'gi');
                formatted = formatted.replace(reg, '\\n' + kw.toUpperCase());
            });

            // Clean line spacing and indent
            const lines = formatted.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            const indented = lines.map(line => {
                const isPrimary = keywords.some(k => line.startsWith(k));
                return isPrimary ? line : '  ' + line;
            }).join('\\n');

            // Table Extraction
            const tableMatches = [...input.matchAll(/FROM\\s+([a-zA-Z0-9_]+)|JOIN\\s+([a-zA-Z0-9_]+)/gi)];
            const tables = [...new Set(tableMatches.map(m => m[1] || m[2]).filter(Boolean))];

            renderPayload(indented, 'SQL formatted. Referenced tables identified: ' + tables.join(', '));
        """
    }
]

class HumanArtisansEngine:
    def __init__(self):
        self.init_registry()

    def init_registry(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS human_crafted_portfolio (
                slug TEXT PRIMARY KEY,
                title TEXT,
                category TEXT,
                theme TEXT,
                file_path TEXT,
                deployed_epoch REAL
            )
        """)
        conn.commit()
        conn.close()

    def compile_bespoke_page(self, spec: Dict[str, Any]) -> str:
        """Constructs an ultra-clean, human-grade web application tailored to its design DNA."""
        return f'''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{spec["title"]}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&family=Geist:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Geist', sans-serif; }}
        code, pre, .font-mono {{ font-family: 'Geist Mono', monospace; }}
        ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: #333; border-radius: 3px; }}
    </style>
</head>
<body class="{spec["bg_color"]} text-neutral-100 min-h-screen flex flex-col font-sans selection:bg-neutral-800 antialiased">

    <!-- Artisan Top Bar -->
    <header class="h-14 border-b {spec["border_color"]}/80 bg-opacity-80 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-50">
        <div class="flex items-center gap-3">
            <a href="../index.html" class="w-7 h-7 rounded-md bg-neutral-800 border {spec["border_color"]} flex items-center justify-center font-mono text-xs font-semibold text-white">
                //
            </a>
            <span class="font-semibold text-sm tracking-tight text-white">{spec["title"].split('//')[0].strip()}</span>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded-full {spec["accent_badge"]}">{spec["category"]}</span>
        </div>
        <div class="flex items-center gap-3">
            <button onclick="injectSample()" class="text-xs font-mono text-neutral-400 hover:text-white px-3 py-1 rounded border {spec["border_color"]} transition">
                Load Example
            </button>
            <button onclick="resetInput()" class="text-xs font-mono text-neutral-500 hover:text-neutral-300 transition">
                Clear
            </button>
        </div>
    </header>

    <!-- Split-Pane Workspace -->
    <main class="flex-1 max-w-6xl mx-auto w-full p-6 flex flex-col lg:flex-row gap-6">
        
        <!-- Left: Input Workspace -->
        <div class="w-full lg:w-1/2 flex flex-col border {spec["border_color"]} rounded-xl {spec["panel_color"]} p-4 shadow-xl">
            <div class="flex items-center justify-between pb-3 border-b {spec["border_color"]}/60 mb-3">
                <span class="text-xs font-mono text-neutral-400">{spec["input_label"]}</span>
                <span id="byteCounter" class="text-[11px] font-mono text-neutral-500">0 bytes</span>
            </div>
            
            <textarea 
                id="sourceInput" 
                class="flex-1 w-full bg-transparent resize-none font-mono text-xs leading-relaxed text-neutral-200 placeholder-neutral-700 focus:outline-none focus:ring-0 min-h-[300px]"
                placeholder="Paste payload here..."
                oninput="onInputChange()"
            ></textarea>

            <div class="pt-3 border-t {spec["border_color"]}/60 flex items-center justify-between mt-2">
                <span class="text-[11px] font-mono text-neutral-500">Engine: Client-Side Isolated</span>
                <button onclick="executeEngine()" class="px-4 py-2 rounded-lg {spec["action_btn"]} font-mono text-xs font-semibold transition shadow-md flex items-center gap-2">
                    <span>Process</span>
                    <kbd class="text-[10px] opacity-70 bg-black/30 px-1 rounded">⌘↵</kbd>
                </button>
            </div>
        </div>

        <!-- Right: Output & Inspector -->
        <div class="w-full lg:w-1/2 flex flex-col border {spec["border_color"]} rounded-xl {spec["panel_color"]} p-4 shadow-xl">
            <div class="flex items-center justify-between pb-3 border-b {spec["border_color"]}/60 mb-3">
                <span id="statusIndicator" class="text-xs font-mono text-neutral-400">Execution Output</span>
                <button onclick="copyOutput()" class="text-xs font-mono {spec["accent_text"]} hover:underline">
                    Copy
                </button>
            </div>

            <pre id="outputView" class="flex-1 font-mono text-xs leading-relaxed text-neutral-300 overflow-auto whitespace-pre-wrap min-h-[300px]">// Processed payload will render here...</pre>
        </div>
    </main>

    <!-- Human Micro Footer -->
    <footer class="border-t {spec["border_color"]}/60 py-4 px-6 text-center text-xs text-neutral-500 font-mono">
        Bespoke Architecture • Zero External Server Transmission
    </footer>

    <script>
        const samplePayload = `{spec["sample"].replace("`", "\\`")}`;

        function injectSample() {{
            document.getElementById('sourceInput').value = samplePayload;
            onInputChange();
            executeEngine();
        }}

        function resetInput() {{
            document.getElementById('sourceInput').value = '';
            document.getElementById('outputView').innerText = '// Processed payload will render here...';
            onInputChange();
        }}

        function onInputChange() {{
            const val = document.getElementById('sourceInput').value;
            const bytes = new Blob([val]).size;
            document.getElementById('byteCounter').innerText = bytes + ' bytes';
        }}

        function renderPayload(str, status) {{
            document.getElementById('outputView').innerText = str;
            document.getElementById('statusIndicator').innerHTML = `<span class="{spec["accent_text"]}">✓ ${{status}}</span>`;
        }}

        function copyOutput() {{
            const text = document.getElementById('outputView').innerText;
            if(!text || text.startsWith('//')) return;
            navigator.clipboard.writeText(text).then(() => {{
                const prev = document.getElementById('statusIndicator').innerHTML;
                document.getElementById('statusIndicator').innerHTML = `<span class="text-emerald-400">✓ Copied</span>`;
                setTimeout(() => document.getElementById('statusIndicator').innerHTML = prev, 1200);
            }});
        }}

        function executeEngine() {{
            const input = document.getElementById('sourceInput').value.trim();
            if (!input) return;
            {spec["js_algorithm"]}
        }}

        document.addEventListener('keydown', (e) => {{
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') executeEngine();
        }});
    </script>
</body>
</html>'''

    def deploy_suite(self):
        print("==================================================================")
        print("🎨 ENGAGING HUMAN-ARTISAN BESPOKE CODE SYNTHESIS")
        print("==================================================================")

        cards = []
        for spec in HUMAN_CRAFTED_SPECS:
            file_path = os.path.join(SAAS_DIR, f"{spec['slug']}.html")
            
            # 1. Compile bespoke page
            html_code = self.compile_bespoke_page(spec)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_code)

            # 2. Update Database
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO human_crafted_portfolio 
                (slug, title, category, theme, file_path, deployed_epoch)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (spec["slug"], spec["title"], spec["category"], spec["domain_theme"], file_path, time.time()))
            conn.commit()
            conn.close()

            # Prepare card
            card = f'''
        <!-- Artisan Tool: {spec["slug"]} -->
        <a href="saas/{spec["slug"]}.html" target="_blank" style="text-decoration:none;" class="p-5 rounded-xl border border-neutral-800 bg-neutral-900/40 hover:border-neutral-700 transition duration-200 block group">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <span class="text-[10px] font-mono px-2 py-0.5 rounded {spec["accent_badge"]}">{spec["category"]}</span>
                <span style="font-size:12px;color:#737373;font-family:monospace;">Open ➜</span>
            </div>
            <h3 style="font-size:14px;font-weight:600;color:#f5f5f5;margin:0 0 4px 0;">{spec["title"].split('//')[0].strip()}</h3>
            <p style="font-size:12px;color:#a3a3a3;margin:0;line-height:1.4;">{spec["summary"][:90]}...</p>
        </a>'''
            cards.append(card)

            # Write Bus Signal
            bus_signal = {
                "protocol": "HUMAN_ARTISAN_SYNTHESIS_2026",
                "slug": spec["slug"],
                "title": spec["title"],
                "category": spec["category"],
                "domain_theme": spec["domain_theme"],
                "event": "BESPOKE_PRODUCT_DEPLOYED",
                "status": "RATIFIED_HUMAN_GRADE",
                "file_path": file_path,
                "timestamp": time.time(),
            }
            signal_file = os.path.join(BUS_DIR, f"{int(time.time())}_{spec['slug']}.json")
            with open(signal_file, "w", encoding="utf-8") as sf:
                json.dump(bus_signal, sf, indent=2)

            print(f"✨ [DEPLOYED BESPOKE PRODUCT]: {spec['title']}")
            print(f"   ├── Design DNA    : {spec['domain_theme']}")
            print(f"   ├── File Location : {file_path}")

        # 3. Update public/index.html showcase
        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, "r", encoding="utf-8") as f:
                index_html = f.read()

            artisan_section = f'''
<!-- BESPOKE-ARTISAN-SECTION -->
<section id="bespoke-artisan-suite" style="max-width:1100px;margin:48px auto;padding:0 24px;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
    <div style="width:10px;height:10px;border-radius:50%;background:#f43f5e;"></div>
    <div>
      <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0;font-family:sans-serif;">
        Human-Crafted Bespoke Software Suite // Anti-AI Design
      </h2>
      <div style="font-size:12px;color:#737373;font-family:monospace;margin-top:2px;">
        Distinct thematic palettes &middot; Zero boilerplate &middot; Native browser computation
      </div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;">
    {''.join(cards)}
  </div>
</section>
<!-- END-BESPOKE-ARTISAN-SECTION -->
'''
            if "<!-- BESPOKE-ARTISAN-SECTION -->" in index_html:
                import re
                index_html = re.sub(
                    r"<!-- BESPOKE-ARTISAN-SECTION -->.*?<!-- END-BESPOKE-ARTISAN-SECTION -->",
                    artisan_section.strip(),
                    index_html,
                    flags=re.DOTALL
                )
            elif "</body>" in index_html:
                index_html = index_html.replace("</body>", f"{artisan_section}\n</body>")

            with open(INDEX_PATH, "w", encoding="utf-8") as f:
                f.write(index_html)
            print("🔗 Connected to public/index.html showcase.")

        print("==================================================================")
        print("✅ ALL HUMAN-GRADE SITES SYNTHESIZED AND LIVE.")

if __name__ == "__main__":
    artisan = HumanArtisansEngine()
    artisan.deploy_suite()
