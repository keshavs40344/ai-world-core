#!/usr/bin/env python3
"""
GENESIS PROGRAMMATIC SEO & SUBPAGE INDEXER
Auto-indexes every single autonomous sub-page for Googlebot and Bingbot.
Generates comprehensive XML Sitemaps with deep metadata.
"""

import os
import sys
import glob
from datetime import datetime

# UTF-8 Console encoding safety for Windows PowerShell
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

BASE_URL = "https://keshavs40344.github.io/ai-world-core"

def build_search_engine_manifest():
    print("🌐 [SEO INDEXER] Constructing Googlebot Sitemap & Semantic Index...")
    all_pages = glob.glob("public/saas/*.html") + glob.glob("public/tools/*.html")
    
    url_blocks = [
        f"""  <url>
    <loc>{BASE_URL}/public/index.html</loc>
    <lastmod>{datetime.utcnow().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""",
        f"""  <url>
    <loc>{BASE_URL}/public/dashboard.html</loc>
    <lastmod>{datetime.utcnow().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>"""
    ]

    for p in sorted(all_pages):
        clean_path = p.replace("\\", "/")
        url_blocks.append(f"""  <url>
    <loc>{BASE_URL}/{clean_path}</loc>
    <lastmod>{datetime.utcnow().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>""")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(url_blocks)}
</urlset>"""

    with open("public/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    print(f"  ✔ Generated public/sitemap.xml with {len(all_pages) + 2} verified endpoints.")

    # Optimized Robots.txt
    robots_txt = f"""User-agent: *
Allow: /
Sitemap: {BASE_URL}/public/sitemap.xml
"""
    with open("public/robots.txt", "w", encoding="utf-8") as f:
        f.write(robots_txt)
    print("  ✔ Optimized public/robots.txt for search crawlers.")

if __name__ == "__main__":
    build_search_engine_manifest()
