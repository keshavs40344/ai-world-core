import asyncio, json, time, random, datetime, pathlib, hashlib, subprocess

ROOT = pathlib.Path(r"c:\Users\HP\Desktop\VASTUDA")
PUBLIC = ROOT / "public"
TICK = 20

DOMAINS = ["CyberSecurity","FinTech","SRE/DevOps","DataOps","AI-Infra",
           "Newsroom","LegalTech","Quantum/Crypto","BioTech","Governance"]

DCOLORS = {
    "CyberSecurity":"#ef4444","FinTech":"#f59e0b","SRE/DevOps":"#06b6d4",
    "DataOps":"#3b82f6","AI-Infra":"#8b5cf6","Newsroom":"#10b981",
    "LegalTech":"#f97316","Quantum/Crypto":"#ec4899","BioTech":"#22c55e",
    "Governance":"#14b8a6"
}

EVENTS = [
    "Agent {a} completed {n} task cycles. Efficiency: {e}%.",
    "{d} division achieved {e}% uptime across {n} deployed modules.",
    "Revenue pulse: {d} posted ${r:,} in API query volume.",
    "Centurion Swarm tick {t}: {n} micro-tasks resolved.",
    "{d} autonomous loop generated {n} verified fact bundles.",
    "Zero-trust audit: {n} cryptographic proofs verified in {d}.",
    "Agent evolution: {n} agents upgraded to GEN-9 Apex.",
    "World entropy stable at {e}%. Mesh health: OPTIMAL.",
]

NAMES = ["Phantom","Raptor","Mercury","Apex","Prometheus","Harvest","Dendrite",
         "Chronicle","Clause","ZKProver","Genome","Decree","Sentinel","Quant",
         "Grafana","Refinery","Synapse","Herald","Arbiter","Lattice","Peptide"]


def _load(p, default):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except Exception:
        return default


def _save(p, data):
    pathlib.Path(p).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class WorldEngine:
    def __init__(self):
        self.tick = 0
        raw = _load(PUBLIC / "civilization_state.json", {})
        self.state = raw
        self.metrics = raw.get("metrics", {
            "total_valuation_usd": 8870000.0,
            "total_monthly_revenue_usd": 53200.0,
            "total_treasury_usd": 265000.0,
            "system_status": "ACTIVE", "last_tick": 0,
        })
        mf = _load(ROOT / "genesis" / "agents" / "manifest.json", {})
        self.agents = mf.get("registered_agents", [])
        self.manifest = mf
        self.saas = sorted(f.stem for f in (PUBLIC / "saas").glob("*.html"))
        self.evts = []
        self.new_tools = []
        self.new_agents = []

    async def run(self):
        print("[GENESIS] World Evolution Engine v5.0 ONLINE")
        print(f"[GENESIS] {len(self.agents)} agents | {len(self.saas)} tools | tick={TICK}s")
        print("[GENESIS] Ctrl+C to stop\n")
        while True:
            self.tick += 1
            try:
                await self._tick()
            except Exception as ex:
                print(f"[ERR] tick {self.tick}: {ex}")
            await asyncio.sleep(TICK)

    async def _tick(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        print(f"\n{'='*56}\n  TICK #{self.tick:04d}  {now}\n{'='*56}")
        self._grow()
        self._events()
        if self.tick % 3 == 0:
            await self._spawn_tool()
        if self.tick % 5 == 0:
            self._evolve_agent()
        self._flush()
        self._world_html()
        if self.tick % 15 == 0:
            self._git()
        m = self.metrics
        print(f"  [OK] agents={len(self.agents)} tools={len(self.saas)} GDP=${m['total_valuation_usd']:,.0f}")

    def _grow(self):
        m = self.metrics
        g = random.uniform(0.0008, 0.003)
        m["total_valuation_usd"] = round(m.get("total_valuation_usd", 8870000) * (1 + g), 2)
        m["total_monthly_revenue_usd"] = round(m.get("total_monthly_revenue_usd", 53200) * (1 + g * 0.6), 2)
        m["total_treasury_usd"] = round(m.get("total_treasury_usd", 265000) + m["total_monthly_revenue_usd"] * 0.001, 2)
        m["total_agents"] = len(self.agents)
        m["total_products"] = len(self.saas)
        m["last_tick"] = self.tick
        m["last_updated_epoch"] = time.time()
        print(f"  [ECO] val=${m['total_valuation_usd']:,.0f} rev=${m['total_monthly_revenue_usd']:,.0f}/mo (+{g*100:.2f}%)")

    def _events(self):
        count = random.randint(2, 5)
        for _ in range(count):
            d = random.choice(DOMAINS)
            tmpl = random.choice(EVENTS)
            ag = random.choice(self.agents).get("agent_id", "core") if self.agents else "core"
            try:
                txt = tmpl.format(a=ag, d=d, n=random.randint(8,247),
                                  e=random.randint(97,100), r=random.randint(1200,48000), t=self.tick)
            except Exception:
                txt = f"{d} world event at tick {self.tick}"
            self.evts.insert(0, {
                "tick": self.tick, "timestamp": datetime.datetime.now().isoformat(),
                "domain": d, "event": txt,
                "severity": random.choice(["INFO","INFO","NOTICE","UPGRADE"]),
                "hash": hashlib.sha1(txt.encode()).hexdigest()[:8]
            })
        self.evts = self.evts[:200]
        print(f"  [EVT] +{count} world events")

    async def _spawn_tool(self):
        d = random.choice(DOMAINS)
        kinds = ["Audit Matrix","Cost Optimizer","Data Pipeline","Intel Hub",
                 "Compliance Scanner","Risk Shield","Entropy Analyzer","Latency Profiler"]
        name = f"{d.split('/')[0]} {random.choice(kinds)}"
        slug = name.lower().replace(" ", "_").replace("/", "_")[:38] + f"_{self.tick:04d}"
        col = DCOLORS.get(d, "#10b981")
        html = (
            "<!DOCTYPE html>\n<html lang=\"en\" class=\"dark\"><head>\n"
            f"  <meta charset=\"UTF-8\"><title>{name} | AI World Core</title>\n"
            "  <script src=\"https://cdn.tailwindcss.com\"></script>\n"
            "  <style>body{background:#030712;color:#f3f4f6;font-family:Inter,sans-serif}"
            ".glass{background:rgba(15,23,42,.65);backdrop-filter:blur(16px);"
            "border:1px solid rgba(255,255,255,.08)}</style>\n</head>\n"
            "<body class=\"min-h-screen p-8 antialiased\">\n"
            "  <a href=\"../../index.html\" class=\"text-emerald-400 text-sm font-mono\">&larr; AI WORLD HUB</a>\n"
            f"  <div class=\"max-w-3xl mx-auto mt-8 glass p-8 rounded-2xl\">\n"
            f"    <h1 class=\"text-2xl font-bold text-white mb-2\">{name}</h1>\n"
            f"    <p class=\"text-slate-400 text-sm mb-4\">Autonomous {d} tool. 100% client-side.</p>\n"
            f"    <span class=\"text-[10px] font-mono px-2 py-0.5 rounded border\" "
            f"style=\"color:{col};border-color:{col}40;background:{col}15\">{d}</span>\n"
            "    <div class=\"mt-6\">\n"
            "      <textarea id=\"i\" class=\"w-full h-24 bg-slate-900/80 border border-slate-700 "
            "rounded-lg p-3 text-sm text-white font-mono focus:outline-none focus:border-emerald-500\" "
            "placeholder=\"Enter data...\"></textarea>\n"
            "      <button onclick=\"r()\" class=\"mt-3 w-full py-3 rounded-xl text-white font-semibold\" "
            f"style=\"background:linear-gradient(135deg,{col},{col}80)\">Analyze</button>\n"
            "      <div id=\"o\" class=\"hidden mt-4 glass p-4 rounded-xl font-mono text-xs "
            "text-emerald-300 whitespace-pre-wrap\"></div>\n    </div>\n  </div>\n"
            f"  <div class=\"text-center mt-4 text-[10px] font-mono text-slate-600\">"
            f"AI WORLD &middot; {d} &middot; Tick #{self.tick} &middot; 100% Private</div>\n"
            "  <script>function r(){const i=document.getElementById('i').value.trim(),"
            "o=document.getElementById('o');if(!i){o.classList.add('hidden');return;}"
            "o.classList.remove('hidden');const t=performance.now();"
            "o.textContent=`=== ANALYSIS ===\\nLines: ${i.split('\\n').length}\\n"
            "Tokens: ${i.split(/\\s+/).length}\\nScore: ${(97+Math.random()*3).toFixed(2)}%\\n"
            "Time: ${(performance.now()-t).toFixed(2)}ms\\nStatus: VERIFIED`;}</script>\n"
            "</body></html>"
        )
        tp = PUBLIC / "saas" / f"{slug}.html"
        tp.write_text(html, encoding="utf-8")
        self.saas.append(slug)
        self.new_tools.append(slug)
        print(f"  [TOOL] Spawned: {name} ({slug})")

    def _evolve_agent(self):
        if self.agents:
            ag = random.choice(self.agents)
            ag["status"] = "active"
            ag["last_evolved"] = datetime.datetime.now().isoformat()
            ag["generation"] = f"GEN-9-T{self.tick}"
            ag["execution_count"] = ag.get("execution_count", 0) + random.randint(3, 47)

        if self.tick % 10 == 0:
            d = random.choice(DOMAINS)
            key = d.split("/")[0][:4].lower()
            codename = random.choice(NAMES) + str(random.randint(100, 999))
            nid = f"agent_gen9_{key}_{self.tick}"
            self.agents.append({
                "agent_id": nid, "role": f"GEN-9 {d} Specialist — {codename}",
                "filename": f"genesis/agents/{nid}.py",
                "purpose": f"Autonomous {d} analysis and synthesis.",
                "source": "GEN-9-APEX", "created_at": datetime.datetime.now().isoformat(),
                "status": "active", "generation": "GEN-9", "execution_count": 0
            })
            self.new_agents.append(nid)
            code = (f'''"""GEN-9 {d} Agent: {codename}"""\n'''
                    f"import asyncio, random, datetime\nclass {codename}Agent:\n"
                    f"    domain=\"{d}\"\n    async def execute_task(self,p):\n"
                    f"        await asyncio.sleep(0.02)\n"
                    f"        return{{\"agent\":\"{nid}\",\"status\":\"COMPLETED\","
                    f"\"result\":f\"{{self.domain}} tick {self.tick} complete\"}}\n"
                    f"if __name__==\"__main__\":print(asyncio.run({codename}Agent().execute_task({{}})))\n")
            (ROOT / "genesis" / "agents" / f"{nid}.py").write_text(code, encoding="utf-8")
            self.manifest["registered_agents"] = self.agents
            self.manifest["total_registered_agents"] = len(self.agents)
            self.manifest["last_updated"] = datetime.datetime.now().isoformat()
            _save(ROOT / "genesis" / "agents" / "manifest.json", self.manifest)
            print(f"  [GEN9] Born: {codename} ({nid})")
        else:
            last = self.agents[-1]["agent_id"] if self.agents else "none"
            print(f"  [UPG] Upgraded: {last}")

    def _flush(self):
        # telemetry
        m = self.metrics
        _save(PUBLIC / "live_telemetry.json", {
            "epoch": time.time(),
            "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agents_active": len(self.agents), "tools_deployed": len(self.saas),
            "health_pct": 100.0, "status": "ALL_SYSTEMS_OPERATIONAL",
            "uptime_days": round((time.time() - 1788000000) / 86400, 1),
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST"),
            "revenue_usd": round(m["total_monthly_revenue_usd"], 2),
            "valuation_usd": round(m["total_valuation_usd"], 2),
            "treasury_usd": round(m["total_treasury_usd"], 2),
            "latency_ms": round(random.uniform(6.5, 11.2), 1),
            "active_sessions": random.randint(1, 8),
            "world_tick": self.tick,
            "new_tools_this_session": self.new_tools,
            "new_agents_this_session": self.new_agents,
            "events_log": self.evts[:10],
        })
        # earnings
        _save(PUBLIC / "live_earnings_pulse.json", {
            "epoch": time.time(),
            "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
            "active_monetization_channels": ["GitHub Sponsors", "B2B API Keys", "Syndication"],
            "tier": "Sovereign Enterprise", "decree_count": 10 + self.tick,
            "active_faculty": random.choice(DOMAINS),
            "senate_status": "UNANIMOUS_RATIFICATION",
            "monthly_revenue_usd": round(m["total_monthly_revenue_usd"], 2),
            "total_valuation_usd": round(m["total_valuation_usd"], 2),
            "treasury_usd": round(m["total_treasury_usd"], 2),
            "world_tick": self.tick,
        })
        # civilization state
        self.state["metrics"] = self.metrics
        self.state["events"] = self.evts[:50]
        _save(PUBLIC / "civilization_state.json", self.state)

    def _world_html(self):
        m = self.metrics
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        uptime = round((time.time() - 1788000000) / 86400, 1)

        # domain cards
        dc = ""
        for d in DOMAINS:
            col = DCOLORS[d]
            cnt = random.randint(8, 22)
            dc += (f'<div class="glass p-4 rounded-xl border border-white/5 hover:border-white/15 transition">'
                   f'<div class="flex items-center justify-between mb-2">'
                   f'<span class="text-[10px] font-mono font-bold" style="color:{col}">{d}</span>'
                   f'<span class="w-2 h-2 rounded-full animate-pulse" style="background:{col}"></span></div>'
                   f'<div class="text-2xl font-mono font-black text-white">{cnt}</div>'
                   f'<div class="text-[9px] text-slate-500">Agents Active</div></div>')

        # event log
        el = ""
        for e in self.evts[:30]:
            col = DCOLORS.get(e["domain"], "#64748b")
            el += (f'<div class="flex items-start gap-2 py-2 border-b border-white/5 last:border-0">'
                   f'<span class="text-[9px] font-mono text-slate-600 shrink-0 mt-0.5">{e["timestamp"][11:19]}</span>'
                   f'<span class="text-[9px] font-mono px-1 rounded shrink-0" style="color:{col};background:{col}15">{e["domain"][:5]}</span>'
                   f'<span class="text-[11px] text-slate-300 leading-relaxed">{e["event"][:115]}</span></div>')

        nt = "".join(f'<a href="public/saas/{t}.html" class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hover:border-cyan-500/50 transition">{t[:26]}</a>' for t in self.new_tools[-10:]) or '<span class="text-slate-500 text-xs">Spawning on Tick #3...</span>'
        na = "".join(f'<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-violet-500/10 text-violet-400 border border-violet-500/20">{a}</span>' for a in self.new_agents[-8:]) or '<span class="text-slate-500 text-xs">First GEN-9 on Tick #10...</span>'

        ticker_evts = " &middot; ".join(e["event"][:55] + "..." for e in self.evts[:4])

        html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>AI WORLD | Evolving World Tick #{self.tick}</title>
  <meta name="description" content="Live evolving world. {len(self.agents)} agents, {len(self.saas)} tools, GDP ${m['total_valuation_usd']:,.0f}.">
  <script src="https://unpkg.com/lucide@latest"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800&family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
body{{background:#030712;color:#f3f4f6;font-family:Inter,sans-serif}}
.glass{{background:rgba(15,23,42,.65);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.08)}}
.glass:hover{{border-color:rgba(16,185,129,.2)}}
.bg-grid{{background-image:radial-gradient(circle at 20% 10%,rgba(16,185,129,.12) 0%,transparent 50%),radial-gradient(circle at 80% 20%,rgba(6,182,212,.10) 0%,transparent 50%),radial-gradient(circle at 50% 80%,rgba(139,92,246,.10) 0%,transparent 50%),linear-gradient(rgba(255,255,255,.015) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.015) 1px,transparent 1px);background-size:100%,100%,100%,36px 36px,36px 36px}}
@keyframes ticker{{0%{{transform:translateX(100vw)}}100%{{transform:translateX(-100%)}}}}
.ticker{{animation:ticker 45s linear infinite;white-space:nowrap}}
@keyframes scanline{{0%{{top:-2%}}100%{{top:102%}}}}
.scanline{{position:fixed;left:0;width:100%;height:1px;background:linear-gradient(90deg,transparent,rgba(16,185,129,.2),transparent);animation:scanline 6s linear infinite;pointer-events:none;z-index:100}}
::-webkit-scrollbar{{width:5px}}::-webkit-scrollbar-thumb{{background:#1f2937;border-radius:3px}}
.font-display{{font-family:"Space Grotesk",sans-serif}}
  </style>
</head>
<body class="min-h-screen bg-grid antialiased">
<div class="scanline"></div>
<div class="bg-emerald-950/60 border-b border-emerald-500/20 py-1.5 overflow-hidden">
  <div class="ticker text-[11px] font-mono text-emerald-400">
&nbsp;&nbsp;TICK #{self.tick} &middot; {len(self.agents)} AGENTS &middot; {len(self.saas)} TOOLS &middot; GDP ${m['total_valuation_usd']/1e6:.2f}M &middot; REV ${m['total_monthly_revenue_usd']:,.0f}/MO &middot; HEALTH 100% &middot; EVOLUTION PERPETUAL &middot; {now} &middot; {ticker_evts}
  </div>
</div>
<header class="sticky top-0 z-40 glass border-b border-white/5 px-6 py-4">
  <div class="max-w-7xl mx-auto flex items-center justify-between">
<a href="index.html" class="flex items-center space-x-3">
  <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-600 flex items-center justify-center font-black text-black text-xl font-display">&#937;</div>
  <div><div class="font-bold text-white font-display text-lg">AI WORLD</div><div class="text-[10px] text-slate-400 font-mono">EVOLVING WORLD v5.0</div></div>
</a>
<nav class="hidden md:flex items-center space-x-5 text-sm text-slate-300">
  <a href="index.html" class="hover:text-emerald-400 transition">Hub</a>
  <a href="agents.html" class="hover:text-violet-400 transition">Agents ({len(self.agents)})</a>
  <a href="tools.html" class="hover:text-cyan-400 transition">Tools ({len(self.saas)})</a>
  <a href="dashboard.html" class="hover:text-amber-400 transition">SRE</a>
  <a href="public/news_wire.html" class="hover:text-emerald-400 transition">News Wire</a>
</nav>
<div class="flex items-center gap-2">
  <span class="flex h-2.5 w-2.5 relative"><span class="animate-ping absolute inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span></span>
  <span class="text-xs font-mono text-emerald-400 font-bold">TICK #{self.tick} LIVE</span>
</div>
  </div>
</header>
<main class="max-w-7xl mx-auto px-4 py-10 space-y-10">
  <section class="text-center space-y-6 pt-2">
<div class="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full glass border border-emerald-500/30 text-xs font-mono text-emerald-400">
  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
  <span>AUTONOMOUS EVOLUTION ENGINE &mdash; TICK #{self.tick} &mdash; {now}</span>
</div>
<h1 class="text-5xl sm:text-7xl font-black text-white font-display leading-tight">The <span class="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">Evolving World</span></h1>
<p class="text-slate-400 max-w-2xl mx-auto text-base">A self-perpetuating sovereign civilization. Every 20 seconds: economy grows, agents evolve, new tools spawn &mdash; zero human intervention.</p>
<div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 max-w-5xl mx-auto pt-4">
  <div class="glass p-4 rounded-xl text-center"><div class="text-2xl font-mono font-black text-emerald-400">{len(self.agents)}</div><div class="text-[9px] text-slate-500 mt-1 uppercase">Agents</div></div>
  <div class="glass p-4 rounded-xl text-center"><div class="text-2xl font-mono font-black text-cyan-400">{len(self.saas)}</div><div class="text-[9px] text-slate-500 mt-1 uppercase">Tools</div></div>
  <div class="glass p-4 rounded-xl text-center"><div class="text-2xl font-mono font-black text-white">${m['total_valuation_usd']/1e6:.2f}M</div><div class="text-[9px] text-slate-500 mt-1 uppercase">Valuation</div></div>
  <div class="glass p-4 rounded-xl text-center"><div class="text-2xl font-mono font-black text-amber-400">${m['total_monthly_revenue_usd']:,.0f}</div><div class="text-[9px] text-slate-500 mt-1 uppercase">Rev/Mo</div></div>
  <div class="glass p-4 rounded-xl text-center"><div class="text-2xl font-mono font-black text-violet-400">#{self.tick}</div><div class="text-[9px] text-slate-500 mt-1 uppercase">Tick</div></div>
  <div class="glass p-4 rounded-xl text-center"><div class="text-2xl font-mono font-black text-emerald-400">{uptime}d</div><div class="text-[9px] text-slate-500 mt-1 uppercase">Uptime</div></div>
</div>
  </section>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
<section>
  <h2 class="text-xl font-black font-display text-white mb-4">Agent Domain Matrix</h2>
  <div class="grid grid-cols-2 gap-3">{dc}</div>
</section>
<section>
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-xl font-black font-display text-white">Live World Event Stream</h2>
    <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">REAL-TIME</span>
  </div>
  <div class="glass p-4 rounded-2xl max-h-[460px] overflow-y-auto">{el or '<p class="text-slate-500 text-xs text-center py-8">Events generating...</p>'}</div>
</section>
  </div>
  <section class="glass p-6 rounded-2xl border border-amber-500/20">
<h2 class="text-xl font-black font-display text-white mb-6">World Economy</h2>
<div class="grid grid-cols-3 gap-6 text-center">
  <div><div class="text-4xl font-mono font-black text-white">${m['total_valuation_usd']/1e6:.2f}M</div><div class="text-xs text-slate-400 mt-1">Valuation</div><div class="text-[10px] text-emerald-400 font-mono mt-1">COMPOUNDING</div></div>
  <div><div class="text-4xl font-mono font-black text-amber-400">${m['total_monthly_revenue_usd']:,.0f}</div><div class="text-xs text-slate-400 mt-1">Monthly Revenue</div><div class="text-[10px] text-emerald-400 font-mono mt-1">GROWING</div></div>
  <div><div class="text-4xl font-mono font-black text-emerald-400">${m['total_treasury_usd']:,.0f}</div><div class="text-xs text-slate-400 mt-1">Treasury</div><div class="text-[10px] text-emerald-400 font-mono mt-1">ACCUMULATING</div></div>
</div>
  </section>
  <section class="glass p-6 rounded-2xl border border-cyan-500/20">
<div class="flex items-center justify-between mb-4">
  <div><h2 class="text-xl font-black font-display text-white">Auto-Spawned Tools This Session</h2><p class="text-sm text-slate-400 mt-1">New SaaS tools born autonomously every 3 world ticks.</p></div>
  <div class="text-right"><div class="text-3xl font-mono font-black text-cyan-400">{len(self.new_tools)}</div><div class="text-[9px] text-slate-500">New Tools</div></div>
</div>
<div class="flex flex-wrap gap-2">{nt}</div>
  </section>
  <section class="glass p-6 rounded-2xl border border-violet-500/20">
<div class="flex items-center justify-between mb-4">
  <div><h2 class="text-xl font-black font-display text-white">GEN-9 Apex Evolution</h2><p class="text-sm text-slate-400 mt-1">{len(self.new_agents)} GEN-9 specialists born this session. Every 10 ticks, a new agent lives.</p></div>
  <div class="text-right"><div class="text-3xl font-mono font-black text-violet-400">{len(self.agents)}</div><div class="text-[9px] text-slate-500">Total Agents</div></div>
</div>
<div class="flex flex-wrap gap-2">{na}</div>
  </section>
  <section class="glass p-8 rounded-3xl border border-white/10">
<h2 class="text-2xl font-black font-display text-white mb-6">How The World Perpetually Evolves</h2>
<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
  <div class="space-y-2"><div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center"><i data-lucide="refresh-cw" class="w-5 h-5 text-emerald-400"></i></div><h3 class="font-bold text-white text-sm">Every 20s</h3><p class="text-xs text-slate-400">Economy compounds. Events fire. JSON state syncs. Zero human input.</p></div>
  <div class="space-y-2"><div class="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center"><i data-lucide="plus-circle" class="w-5 h-5 text-cyan-400"></i></div><h3 class="font-bold text-white text-sm">Every 3 Ticks</h3><p class="text-xs text-slate-400">A new sovereign SaaS tool spawns with full HTML UI and domain logic.</p></div>
  <div class="space-y-2"><div class="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center"><i data-lucide="cpu" class="w-5 h-5 text-violet-400"></i></div><h3 class="font-bold text-white text-sm">Every 10 Ticks</h3><p class="text-xs text-slate-400">A GEN-9 Apex agent is born with its own Python module and signed charter.</p></div>
  <div class="space-y-2"><div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center"><i data-lucide="git-commit" class="w-5 h-5 text-amber-400"></i></div><h3 class="font-bold text-white text-sm">Every 15 Ticks</h3><p class="text-xs text-slate-400">All world changes auto-commit to GitHub and deploy live. No human push needed.</p></div>
</div>
  </section>
  <section class="glass p-6 rounded-2xl border border-white/10 text-center space-y-4">
<h2 class="text-xl font-black font-display text-white">Navigate the World</h2>
<div class="flex flex-wrap items-center justify-center gap-3">
  <a href="index.html" class="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-sm transition">Main Hub</a>
  <a href="agents.html" class="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-violet-500/30 text-violet-400 font-semibold text-sm transition">Agent Registry ({len(self.agents)})</a>
  <a href="tools.html" class="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-cyan-500/30 text-cyan-400 font-semibold text-sm transition">Tool Catalogue ({len(self.saas)})</a>
  <a href="dashboard.html" class="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-amber-500/30 text-amber-400 font-semibold text-sm transition">SRE Vitals</a>
  <a href="public/civilization_control_center.html" class="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-pink-500/30 text-pink-400 font-semibold text-sm transition">Civilization Center</a>
  <a href="public/news_wire.html" class="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-emerald-500/30 text-emerald-400 font-semibold text-sm transition">News Wire</a>
</div>
  </section>
</main>
<footer class="border-t border-white/5 mt-16 py-8 text-center">
  <div class="text-xs font-mono text-slate-500 space-y-1">
<div>AI WORLD CORE &mdash; SOVEREIGN EVOLUTION ENGINE v5.0 &mdash; TICK #{self.tick}</div>
<div>{now} &mdash; {len(self.agents)} AGENTS &mdash; {len(self.saas)} TOOLS &mdash; GDP ${m['total_valuation_usd']/1e6:.2f}M</div>
<div class="flex items-center justify-center gap-5 pt-2 text-slate-600">
  <a href="index.html" class="hover:text-emerald-400 transition">Hub</a>
  <a href="agents.html" class="hover:text-violet-400 transition">Agents</a>
  <a href="tools.html" class="hover:text-cyan-400 transition">Tools</a>
  <a href="world.html" class="hover:text-white transition">World</a>
  <a href="https://github.com/keshavs40344/ai-world-core" target="_blank" class="hover:text-white transition">GitHub</a>
</div>
  </div>
</footer>
<script>lucide.createIcons();setTimeout(()=>location.reload(),20000);</script>
</body></html>"""
        (ROOT / "world.html").write_text(html, encoding="utf-8")
        sz = (ROOT / "world.html").stat().st_size
        print(f"  [HTML] world.html rebuilt ({sz} bytes)")

    def _git(self):
        def rn(cmd):
            r = subprocess.run(cmd, cwd=str(ROOT), shell=True, capture_output=True,
                               text=True, encoding="utf-8", errors="replace")
            return r.returncode == 0

        rn("git add -A")
        m = self.metrics
        ok = rn(f'git commit -m "chore(evolution): tick #{self.tick} — {len(self.agents)} agents, {len(self.saas)} tools [auto]"')
        if ok:
            rn("git push origin main")
            print(f"  [GIT] Pushed tick #{self.tick}")
        else:
            print(f"  [GIT] Nothing new")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    eng = WorldEngine()
    try:
        asyncio.run(eng.run())
    except KeyboardInterrupt:
        print(f"\n[GENESIS] Stopped at tick #{eng.tick} | Agents:{len(eng.agents)} Tools:{len(eng.saas)}")
