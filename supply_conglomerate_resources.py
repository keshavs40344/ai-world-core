#!/usr/bin/env python3
"""
GENESIS SUPPLY DISPATCHER
Delivers core shared assets, SEO schemas, and utility modules
directly into the production environment.
"""

import os
import sys

# UTF-8 Console encoding safety
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

os.makedirs("public/assets", exist_ok=True)
os.makedirs("public/specs", exist_ok=True)

# 1. Dispatch Core Shared Runtime
core_js_path = "public/assets/genesis_core_lib.js"
core_js_content = """/**
 * GENESIS ENTERPRISE SHARED RUNTIME v1.0
 * Zero-dependency universal export and conversion utilities.
 */
window.GenesisCore = {
    // 1. Instant Clean Clipboard Copy
    copyToClipboard: function(text, feedbackId) {
        if (!navigator.clipboard) {
            const ta = document.createElement('textarea');
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            const el = document.getElementById(feedbackId);
            if (el) {
                const prev = el.innerText;
                el.innerText = "✔ Copied!";
                setTimeout(() => { el.innerText = prev; }, 1800);
            }
            return;
        }
        navigator.clipboard.writeText(text).then(() => {
            const el = document.getElementById(feedbackId);
            if (el) {
                const prev = el.innerText;
                el.innerText = "✔ Copied!";
                setTimeout(() => { el.innerText = prev; }, 1800);
            }
        });
    },

    // 2. Direct Client-Side JSON / Text / CSV File Downloader
    downloadFile: function(filename, content, mimeType = 'text/plain') {
        const blob = new Blob([content], { type: mimeType });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);
    },

    // 3. Tabular CSV to JSON In-Memory Converter
    csvToJson: function(csvText) {
        const lines = csvText.trim().split('\\n');
        if (lines.length < 2) return [];
        const headers = lines[0].split(',').map(h => h.trim().replace(/^["']|["']$/g, ''));
        return lines.slice(1).map(line => {
            const values = line.split(',').map(v => v.trim().replace(/^["']|["']$/g, ''));
            return headers.reduce((acc, h, i) => {
                acc[h] = values[i] || "";
                return acc;
            }, {});
        });
    },

    // 4. Standard NPCI Pre-Filled UPI Paywall Invoker
    triggerPaywall: function(amount = "299.00", note = "Genesis_Pro_Upgrade") {
        const vpa = "";
        const payee = "Keshav";
        const uri = `https://github.com/sponsors/keshavs40344
        window.location.href = uri;
    }
};
"""

with open(core_js_path, "w", encoding="utf-8") as f:
    f.write(core_js_content)
print(f"[SUPPLIED] Shared Utility Runtime: {core_js_path}")

# 2. Dispatch Enterprise Robots & Crawler Directives
robots_txt = """User-agent: *
Allow: /
Sitemap: https://keshavs40344.github.io/ai-world-core/public/sitemap.xml
"""
with open("public/robots.txt", "w", encoding="utf-8") as f:
    f.write(robots_txt)
print("[SUPPLIED] SEO Robots.txt Configured")
