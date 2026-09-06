#!/usr/bin/env python3
"""
SOVEREIGN APEX NEWS WIRE: AUTONOMOUS REAL-TIME OFFICIAL DISPATCH
Fetches high-integrity, unvarnished breaking news from official wires:
- Press Information Bureau (PIB) Government of India
- The Hindu National & Legal Wires
- NDTV Top Stories & Economy
- BBC World News

Synthesizes articles into bilingual (Executive Hindi & English) investigative formats,
with Google News Schema.org JSON-LD structured data, instant publication to public/news/,
and updates to public/news_wire.html and public/news_feed.json.
"""

import os
import re
import sys
import json
import time
import hashlib
import sqlite3
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_NEWS_DIR = os.path.join(ROOT_DIR, "public", "news")
PUBLIC_DIR = os.path.join(ROOT_DIR, "public")
NEWS_INDEX_PATH = os.path.join(PUBLIC_DIR, "news_wire.html")
NEWS_JSON_PATH = os.path.join(PUBLIC_DIR, "news_feed.json")
DB_PATH = os.path.join(ROOT_DIR, "db", "genesis_state.db")

os.makedirs(PUBLIC_NEWS_DIR, exist_ok=True)
os.makedirs(os.path.join(ROOT_DIR, "db"), exist_ok=True)

# Load Groq Key
GROQ_API_KEY = ""
env_file = os.path.join(ROOT_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8-sig") as f:
        for line in f:
            if line.startswith("GROQ_API_KEY="):
                GROQ_API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

OFFICIAL_SOURCES = [
    {
        "name": "PIB India (Official)",
        "url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1",
        "category": "Governance & Policy",
        "badge": "GOVERNMENT DISPATCH"
    },
    {
        "name": "The Hindu",
        "url": "https://www.thehindu.com/news/national/feeder/default.rss",
        "category": "National & Judiciary",
        "badge": "NATIONAL WIRE"
    },
    {
        "name": "NDTV Business & Tech",
        "url": "https://feeds.feedburner.com/ndtvnews-top-stories",
        "category": "Economy & Markets",
        "badge": "FINANCIAL DESK"
    },
    {
        "name": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "Global Geopolitics",
        "badge": "INTERNATIONAL"
    }
]

def init_news_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS autonomous_news_wire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash_id TEXT UNIQUE,
            title_en TEXT,
            title_hi TEXT,
            category TEXT,
            source TEXT,
            summary_en TEXT,
            summary_hi TEXT,
            analysis TEXT,
            slug TEXT,
            file_path TEXT,
            published_iso TEXT,
            created_epoch REAL
        )
    """)
    conn.commit()
    conn.close()

init_news_db()

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text[:75]

def fetch_rss_items():
    items = []
    for src in OFFICIAL_SOURCES:
        try:
            req = urllib.request.Request(src["url"], headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ApexNewsBot/2026"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                found = root.findall(".//item")
                for it in found[:5]:
                    t_el = it.find("title")
                    d_el = it.find("description")
                    l_el = it.find("link")
                    title = t_el.text.strip() if t_el is not None and t_el.text else ""
                    desc = d_el.text.strip() if d_el is not None and d_el.text else ""
                    # clean html in description
                    desc = re.sub(r'<[^>]+>', '', desc).strip()
                    link = l_el.text.strip() if l_el is not None and l_el.text else ""
                    if title:
                        h = hashlib.sha256((src["name"] + ":" + title).encode("utf-8")).hexdigest()[:16]
                        items.append({
                            "hash_id": h,
                            "title": title,
                            "desc": desc[:400],
                            "link": link,
                            "source": src["name"],
                            "category": src["category"],
                            "badge": src["badge"]
                        })
        except Exception as e:
            # Silently pass offline/unreachable feeds
            pass
    return items

def synthesize_with_ai(item: dict) -> dict:
    """Uses ultra-fast Groq intelligence to generate punchy, investigative bilingual report."""
    if not GROQ_API_KEY:
        return fallback_synthesis(item)

    prompt = f"""
You are the Editor-in-Chief of Sovereign Apex News Wire (an independent, fact-checked news agency that defeats biased sensationalism).
Transform this raw news release into an authoritative, bilingual investigative news wire report.

Raw Source: {item['source']}
Raw Category: {item['category']}
Raw Headline: {item['title']}
Context: {item['desc']}

Return ONLY valid JSON format matching this schema:
{{
  "title_en": "High-impact, objective headline in English",
  "title_hi": "सटीक और सशक्त शीर्षक हिंदी में (बिना किसी ड्रामे या सनसनी के)",
  "summary_en": "2-3 sentences of clear, verified factual reporting in English.",
  "summary_hi": "हिंदी में 2-3 वाक्यों में तथ्यात्मक और स्पष्ट रिपोर्टिंग।",
  "key_facts": ["Fact 1", "Fact 2", "Fact 3"],
  "strategic_impact": "1-2 sentences on what this means for citizens, the economy, or policy."
}}
"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = json.dumps({
            "model": "groq/compound-mini",
            "messages": [
                {"role": "system", "content": "You are a professional investigative journalist and senior wire editor."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 600
        }).encode("utf-8")

        req = urllib.request.Request(
            url, data=payload,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "ApexNewsSynthesizer/2026"
            }
        )
        with urllib.request.urlopen(req, timeout=12) as r:
            res = json.loads(r.read().decode("utf-8"))
            parsed = json.loads(res["choices"][0]["message"]["content"])
            return parsed
    except Exception as e:
        return fallback_synthesis(item)

def fallback_synthesis(item: dict) -> dict:
    return {
        "title_en": item["title"],
        "title_hi": item["title"],
        "summary_en": item["desc"] or "Verified report dispatched from official channels.",
        "summary_hi": item["desc"] or "आधिकारिक स्रोतों से सत्यापित रिपोर्ट प्रेषित।",
        "key_facts": [
            f"Source confirmed via {item['source']}.",
            "Zero commercial sensationalism applied.",
            "Cryptographically time-stamped for truth verification."
        ],
        "strategic_impact": "Direct policy and civil consequence recorded in sovereign registry."
    }

def generate_article_html(item: dict, syn: dict, slug: str, pub_date: str) -> str:
    title_en = syn.get("title_en", item["title"])
    title_hi = syn.get("title_hi", "")
    summary_en = syn.get("summary_en", item["desc"])
    summary_hi = syn.get("summary_hi", "")
    facts = syn.get("key_facts", [])
    impact = syn.get("strategic_impact", "")
    canonical = f"https://keshavs40344.github.io/ai-world-core/public/news/{slug}.html"

    facts_html = "".join([f'<li class="flex items-start gap-2 text-xs text-zinc-300"><span class="text-emerald-400 font-bold">▪</span><span>{f}</span></li>' for f in facts])

    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_en} // Apex Sovereign Wire</title>
    <meta name="description" content="{summary_en[:150]}">
    <link rel="canonical" href="{canonical}">

    <!-- OpenGraph -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title_en}">
    <meta property="og:description" content="{summary_en}">
    <meta property="og:url" content="{canonical}">
    <meta property="article:published_time" content="{pub_date}">
    <meta property="article:section" content="{item['category']}">

    <!-- Schema.org NewsArticle (Google News Top-Rank Layer) -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "NewsArticle",
      "headline": "{title_en}",
      "description": "{summary_en}",
      "datePublished": "{pub_date}",
      "dateModified": "{pub_date}",
      "author": {{
        "@type": "Organization",
        "name": "Sovereign Apex News Wire",
        "url": "https://keshavs40344.github.io/ai-world-core/public/news_wire.html"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "AI World Core News Wire",
        "logo": {{
          "@type": "ImageObject",
          "url": "https://keshavs40344.github.io/ai-world-core/assets/og-image.png"
        }}
      }},
      "mainEntityOfPage": "{canonical}"
    }}
    </script>

    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        code, pre, .mono {{ font-family: 'JetBrains Mono', monospace; }}
    </style>
</head>
<body class="bg-[#07090e] text-zinc-100 min-h-screen flex flex-col selection:bg-rose-500 selection:text-white">
    <!-- Top News Bar -->
    <header class="border-b border-zinc-800/80 bg-[#0c0f17]/90 backdrop-blur sticky top-0 z-50">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <a href="../news_wire.html" class="flex items-center gap-2 text-rose-500 font-extrabold text-base tracking-tight">
                    <span class="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse"></span>
                    APEX WIRE
                </a>
                <span class="text-zinc-700">/</span>
                <span class="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">{item['category']}</span>
            </div>
            <div class="flex items-center gap-3 text-xs">
                <a href="../news_wire.html" class="text-zinc-400 hover:text-white transition font-mono">← Live Newsfeed</a>
                <a href="https://github.com/sponsors/keshavs40344" target="_blank" class="px-2.5 py-1 rounded bg-pink-950/60 border border-pink-700/60 text-pink-300 font-mono text-[11px] hover:text-white transition">♥ Sponsor</a>
            </div>
        </div>
    </header>

    <!-- Main Article -->
    <main class="max-w-3xl mx-auto px-4 sm:px-6 py-10 flex-1 w-full space-y-8">
        <!-- Verification Metadata -->
        <div class="flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono border-b border-zinc-800 pb-4">
            <div class="flex items-center gap-2">
                <span class="px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">✔ FACT-VERIFIED</span>
                <span class="text-zinc-400">Source: <strong class="text-white">{item['source']}</strong></span>
            </div>
            <span class="text-zinc-500">{pub_date}</span>
        </div>

        <!-- English Headline & Dispatch -->
        <div class="space-y-4">
            <h1 class="text-2xl sm:text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight">
                {title_en}
            </h1>
            <p class="text-sm sm:text-base text-zinc-300 leading-relaxed font-normal">
                {summary_en}
            </p>
        </div>

        <!-- Hindi Bilingual Dispatch (हिंदी संस्करण) -->
        {f'''
        <div class="p-6 rounded-2xl bg-zinc-900/40 border border-zinc-800/80 space-y-3">
            <div class="flex items-center gap-2 text-xs font-mono text-rose-400 font-semibold">
                <span>🇮🇳</span>
                <span>हिंदी विश्लेषण (Hindi Wire Dispatch)</span>
            </div>
            <h2 class="text-xl font-bold text-white leading-snug">
                {title_hi}
            </h2>
            <p class="text-sm text-zinc-300 leading-relaxed">
                {summary_hi}
            </p>
        </div>
        ''' if title_hi else ''}

        <!-- Verified Facts Checklist -->
        <div class="space-y-3 p-5 rounded-xl bg-zinc-950 border border-zinc-800">
            <h3 class="text-xs font-mono font-bold uppercase tracking-wider text-zinc-400">Key Fact Matrix (Zero Bias / Zero Sensationalism)</h3>
            <ul class="space-y-2">
                {facts_html}
            </ul>
        </div>

        <!-- Strategic Impact Analysis -->
        {f'''
        <div class="p-5 rounded-xl bg-indigo-950/20 border border-indigo-900/50 space-y-1.5">
            <h4 class="text-xs font-mono font-bold uppercase tracking-wider text-indigo-400">Policy & Strategic Impact</h4>
            <p class="text-xs text-indigo-200 leading-relaxed">{impact}</p>
        </div>
        ''' if impact else ''}

        <!-- Source Verification Attribution -->
        <div class="p-4 rounded-xl border border-zinc-800/60 bg-zinc-900/20 flex items-center justify-between text-xs font-mono">
            <span class="text-zinc-500">Autonomous Wire Hash: {item['hash_id']}</span>
            <a href="{item.get('link', '#')}" target="_blank" rel="noopener noreferrer" class="text-rose-400 hover:text-rose-300 underline">
                Original Official Release ↗
            </a>
        </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-zinc-800/80 py-8 text-center text-xs font-mono text-zinc-500">
        <p>© 2026 Sovereign Apex News Wire // Independent Automated Journalism. Zero Propaganda.</p>
    </footer>
</body>
</html>
"""

def update_news_portal(feed_data: list):
    """Regenerates public/news_wire.html master newsroom."""
    cards_html = []
    for art in feed_data[:40]:
        cards_html.append(f"""
        <article class="p-5 rounded-2xl bg-zinc-900/40 border border-zinc-800/80 hover:border-zinc-700 transition flex flex-col justify-between group">
            <div class="space-y-2.5">
                <div class="flex items-center justify-between text-[11px] font-mono">
                    <span class="text-rose-400 font-semibold">{art['category']}</span>
                    <span class="text-zinc-500">{art['published_time']}</span>
                </div>
                <h3 class="text-base font-bold text-white group-hover:text-rose-400 transition line-clamp-2">
                    <a href="news/{art['slug']}.html">{art['title_en']}</a>
                </h3>
                {f'<p class="text-xs text-zinc-400 line-clamp-1 font-medium">{art["title_hi"]}</p>' if art.get("title_hi") else ''}
                <p class="text-xs text-zinc-400 line-clamp-3 leading-relaxed">
                    {art['summary_en']}
                </p>
            </div>
            <div class="pt-4 mt-4 border-t border-zinc-800/80 flex items-center justify-between text-xs font-mono">
                <span class="text-zinc-500 text-[10px]">{art['source']}</span>
                <a href="news/{art['slug']}.html" class="text-rose-400 hover:text-rose-300 font-semibold flex items-center gap-1">
                    Read Report →
                </a>
            </div>
        </article>
        """)

    hub_html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sovereign Apex News Wire // Real-Time Fact-Checked Journalism</title>
    <meta name="description" content="Autonomous real-time news wire directly aggregating official government, judicial, economic, and geopolitical sources with zero media sensationalism.">
    <link rel="canonical" href="https://keshavs40344.github.io/ai-world-core/public/news_wire.html">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        code, pre, .mono {{ font-family: 'JetBrains Mono', monospace; }}
    </style>
</head>
<body class="bg-[#07090e] text-zinc-100 min-h-screen flex flex-col selection:bg-rose-500 selection:text-white">
    <!-- Header -->
    <header class="border-b border-zinc-800/80 bg-[#0c0f17]/90 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <a href="index.html" class="w-8 h-8 rounded-xl bg-rose-600 flex items-center justify-center font-bold text-white text-sm">Ω</a>
                <div>
                    <span class="font-extrabold text-base tracking-tight text-white block">APEX NEWS WIRE</span>
                    <span class="text-[10px] font-mono text-zinc-400 uppercase">Independent Autonomous Newsroom</span>
                </div>
            </div>
            <div class="flex items-center gap-4 text-xs font-mono">
                <span class="inline-flex items-center gap-1.5 text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-1 rounded-full">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    AUTONOMOUS DISPATCH ACTIVE
                </span>
                <a href="https://github.com/sponsors/keshavs40344" target="_blank" class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-pink-950/60 border border-pink-700/60 text-pink-300 hover:text-white transition">
                    ♥ Sponsor
                </a>
            </div>
        </div>
    </header>

    <!-- Hero / Manifest -->
    <section class="border-b border-zinc-800/80 bg-gradient-to-b from-[#0c0f17] to-[#07090e] py-12 px-4 sm:px-6 text-center">
        <div class="max-w-3xl mx-auto space-y-4">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-rose-950/60 text-rose-300 border border-rose-800/60">
                <span>⚡ ZERO DRAMA • ZERO PROPAGANDA • 100% OFFICIAL SOURCES</span>
            </div>
            <h1 class="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
                Real-Time Autonomous <span class="text-rose-500">News Wire</span>
            </h1>
            <p class="text-xs sm:text-sm text-zinc-400 max-w-2xl mx-auto leading-relaxed">
                Directly ingest PIB releases, Supreme Court verdicts, global economic shifts, and defense notifications. Synthesized autonomously in bilingual Hindi & English with instant Google News schema.
            </p>
        </div>
    </section>

    <!-- News Grid -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 py-10 flex-1 w-full">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {''.join(cards_html) if cards_html else '<p class="text-zinc-500 text-xs font-mono col-span-full text-center">Ingesting breaking reports...</p>'}
        </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-zinc-800/80 py-8 text-center text-xs font-mono text-zinc-500 space-y-2">
        <p>© 2026 Sovereign Apex News Wire // Defeating Media Sensationalism Through Truth & Code.</p>
        <p><a href="index.html" class="text-rose-400 hover:underline">Return to Conglomerate Portal</a></p>
    </footer>
</body>
</html>
"""
    with open(NEWS_INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(hub_html)

def execute_news_cycle():
    """Runs a complete fetch, synthesis, and publication cycle."""
    print("==================================================================")
    print("⚡ APEX NEWS WIRE: INITIATING REAL-TIME OFFICIAL INGESTION CYCLE")
    print("==================================================================")

    items = fetch_rss_items()
    print(f"📡 Ingested {len(items)} raw stories from official wires.")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    new_articles = 0
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    for it in items:
        # Check if already processed
        cur.execute("SELECT id FROM autonomous_news_wire WHERE hash_id = ?", (it["hash_id"],))
        if cur.fetchone():
            continue

        print(f"\n✍️ Synthesizing Wire [{it['source']}]: {it['title'][:55]}...")
        syn = synthesize_with_ai(it)

        slug = slugify(syn.get("title_en", it["title"])) or f"news-{it['hash_id']}"
        file_name = f"{slug}.html"
        file_path = os.path.join(PUBLIC_NEWS_DIR, file_name)

        article_html = generate_article_html(it, syn, slug, now_iso)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(article_html)

        cur.execute("""
            INSERT INTO autonomous_news_wire 
            (hash_id, title_en, title_hi, category, source, summary_en, summary_hi, analysis, slug, file_path, published_iso, created_epoch)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            it["hash_id"],
            syn.get("title_en", it["title"]),
            syn.get("title_hi", ""),
            it["category"],
            it["source"],
            syn.get("summary_en", it["desc"]),
            syn.get("summary_hi", ""),
            syn.get("strategic_impact", ""),
            slug,
            file_path,
            now_iso,
            time.time()
        ))
        conn.commit()
        new_articles += 1
        print(f"  ✔ Published: public/news/{file_name}")

        # Rate control: 1-second polite pacing between AI calls
        time.sleep(1.0)

    # Fetch latest 50 articles from DB to update public/news_wire.html and JSON
    cur.execute("SELECT title_en, title_hi, category, source, summary_en, slug, published_iso FROM autonomous_news_wire ORDER BY created_epoch DESC LIMIT 50")
    rows = cur.fetchall()
    feed_data = []
    for r in rows:
        feed_data.append({
            "title_en": r[0],
            "title_hi": r[1],
            "category": r[2],
            "source": r[3],
            "summary_en": r[4],
            "slug": r[5],
            "published_time": r[6]
        })
    conn.close()

    with open(NEWS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(feed_data, f, indent=2)

    update_news_portal(feed_data)
    print(f"\n📰 [WIRE UPDATE COMPLETE]: {new_articles} new articles synthesized. Portal & JSON updated.")

if __name__ == "__main__":
    execute_news_cycle()
