#!/usr/bin/env python3
"""
GENESIS GLOBAL PAYMENT & AUTH INJECTOR
Upgrades all SaaS and Tools pages to use the bulletproof Omnichannel Checkout
and Sovereign Authentication Engine.
"""

import os
import sys
import glob
import re

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

def patch_page(file_path: str):
    if not file_path.endswith(".html"):
        return

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    modified = False

    # 1. Ensure genesis_payments_auth.js is imported
    if "genesis_payments_auth.js" not in content:
        if "</head>" in content:
            script_tag = '    <script src="../assets/genesis_payments_auth.js"></script>\n</head>' if ("saas" in file_path or "tools" in file_path) else '    <script src="assets/genesis_payments_auth.js"></script>\n</head>'
            content = content.replace("</head>", script_tag)
            modified = True

    # 2. Add Auth Widget placeholder in headers if not present
    if "genesisAuthWidget" not in content and "<header" in content:
        # Match header action containers
        header_patterns = [
            r"(<div class=[\"'][^\"']*flex items-center gap-3[\"'][^>]*>)",
            r"(<div class=[\"'][^\"']*flex items-center space-x-3[\"'][^>]*>)",
            r"(<div class=[\"'][^\"']*flex items-center space-x-4[\"'][^>]*>)"
        ]
        for pat in header_patterns:
            if re.search(pat, content):
                content = re.sub(
                    pat,
                    r'\1\n                <div id="genesisAuthWidget"></div>',
                    content,
                    count=1
                )
                modified = True
                break

    # 3. Replace old triggerPaywallModal with GenesisCheckout.open()
    if "triggerPaywallModal" in content:
        content = content.replace("triggerPaywallModal()", "GenesisCheckout.open({ amount: '299.00' })")
        content = content.replace("onclick=\"triggerPaywallModal()\"", "onclick=\"GenesisCheckout.open({ amount: '299.00' })\"")
        modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✔ Upgraded with Omnichannel Checkout & Auth: {file_path}")

def run():
    print("🚀 [UPGRADE CYCLE] Injecting Universal Payment Gateway and Auth into all assets...")
    targets = sorted(glob.glob("public/**/*.html", recursive=True))
    for t in targets:
        patch_page(t)
    print("✅ All assets now locked directly to keshavthakur07@ptyes with multi-app payment and auth.")

if __name__ == "__main__":
    run()
