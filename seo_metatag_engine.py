#!/usr/bin/env python3
"""
GENESIS SEO & SOCIAL GRAPH INJECTOR
Scans all standalone tools and SaaS pages, injecting standard OpenGraph,
Twitter Cards, and JSON-LD schema for social media and search rankings.
"""

import os
import sys
import glob
import re
import urllib.parse

# UTF-8 Console encoding safety
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "https://keshavs40344.github.io/ai-world-core"

def generate_seo_block(title: str, description: str, page_url: str) -> str:
    clean_title = title.replace('"', '&quot;')
    clean_desc = description.replace('"', '&quot;')
    encoded_title = urllib.parse.quote(title[:40])
    dynamic_og_img = f"https://placehold.co/1200x630/020617/6366f1/png?text={encoded_title}+Studio&font=montserrat"

    return f"""
    <!-- DYNAMIC SEO & SOCIAL GRAPH (Auto-Injected) -->
    <meta name="title" content="{clean_title}">
    <meta name="description" content="{clean_desc}">

    <!-- Open Graph / Facebook / LinkedIn / WhatsApp -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{page_url}">
    <meta property="og:title" content="{clean_title}">
    <meta property="og:description" content="{clean_desc}">
    <meta property="og:image" content="{dynamic_og_img}">

    <!-- Twitter / X -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{page_url}">
    <meta name="twitter:title" content="{clean_title}">
    <meta name="twitter:description" content="{clean_desc}">
    <meta name="twitter:image" content="{dynamic_og_img}">

    <!-- JSON-LD Structured Data for Googlebot -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": "{clean_title}",
      "url": "{page_url}",
      "description": "{clean_desc}",
      "applicationCategory": "DeveloperApplication",
      "operatingSystem": "All modern browsers",
      "offers": {{
        "@type": "Offer",
        "price": "0.00",
        "priceCurrency": "USD"
      }}
    }}
    </script>
    <!-- /SEO BLOCK -->
    """

def process_html_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already injected
    if "DYNAMIC SEO & SOCIAL GRAPH" in content:
        return False

    # Extract Title
    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        slug = os.path.basename(file_path).replace(".html", "")
        title = slug.replace("_", " ").title() + " — Genesis Autonomous Suite"

    # Description
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
    if desc_match:
        description = desc_match.group(1).strip()
    else:
        description = f"100% Client-side utility for {title}. High-speed, private, zero-server data leakage."

    # Construct Public URL
    rel_path = os.path.relpath(file_path, start="public").replace("\\", "/")
    full_url = f"{BASE_URL}/{rel_path}" if not rel_path.startswith("index.html") else BASE_URL

    seo_tags = generate_seo_block(title, description, full_url)

    # Inject right before </head>
    if "</head>" in content:
        new_content = content.replace("</head>", f"{seo_tags}\n</head>")
    elif "<body" in content:
        new_content = re.sub(r"(<body[^>]*>)", f"{seo_tags}\n\\1", content, count=1, flags=re.IGNORECASE)
    else:
        new_content = seo_tags + "\n" + content

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True

def run():
    print("[SEO ENGINE] Auditing and injecting OpenGraph meta cards across all assets...")
    targets = glob.glob("public/**/*.html", recursive=True)
    injected = 0
    for p in targets:
        if process_html_file(p):
            injected += 1
            print(f"  [OK] Injected tags: {p}")
    print(f"[COMPLETE] {injected} pages upgraded with social graph tags.")

if __name__ == "__main__":
    run()
