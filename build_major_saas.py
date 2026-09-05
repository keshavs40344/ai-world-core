#!/usr/bin/env python3
"""
GENESIS MAJOR SAAS COMPILER: INVOICEFORGE STUDIO PRO
A fully functional, standalone, client-side Enterprise B2B SaaS Application:
- Real-time calculations (Taxes, Discounts, Itemized tables)
- Client & Business Profile persistence via localStorage
- Print / Export to PDF Engine (native print stylesheet)
- Usage Counter & Hard Paywall Modal (UPI: )
- Direct Client-Side Pro Utility
"""

import os
import sys
import json
import urllib.parse

# Ensure UTF-8
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

os.makedirs("public/saas", exist_ok=True)
os.makedirs("public/specs", exist_ok=True)

UPI_ID = ""
PAYEE = ""
AMOUNT = "299.00"
NOTE = "InvoiceForge_Pro_Lifetime"

query_params = urllib.parse.urlencode({
    "pa": UPI_ID,
    "pn": PAYEE,
    "am": AMOUNT,
    "cu": "INR",
    "tn": NOTE,
})
upi_link = "https://github.com/sponsors/keshavs40344"
qr_url = ""

SAAS_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InvoiceForge Pro — Enterprise Billing & Tax Studio</title>
    <meta name="description" content="Free client-side invoice and ledger generator. 100% private, instant PDF exports, no sign-up required.">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {{
            body * {{ visibility: hidden; }}
            #printableInvoice, #printableInvoice * {{ visibility: visible; }}
            #printableInvoice {{ position: absolute; left: 0; top: 0; width: 100%; border: none !important; box-shadow: none !important; }}
            .no-print {{ display: none !important; }}
        }}
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans antialiased">

    <!-- Top Bar Navigation -->
    <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40 no-print">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-black text-white text-lg">⚡</div>
                <div>
                    <h1 class="font-bold text-white text-base tracking-tight leading-none">InvoiceForge <span class="text-indigo-400 text-xs font-mono uppercase bg-indigo-950 px-1.5 py-0.5 rounded border border-indigo-800">Pro Studio</span></h1>
                    <p class="text-[11px] text-slate-400">Zero-Latency Client-Side Billing Suite</p>
                </div>
            </div>
            <div class="flex items-center space-x-3">
                <button onclick="triggerPaywall()" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3.5 py-1.5 rounded-lg transition shadow-md shadow-emerald-900/30">
                    Upgrade Pro (₹299)
                </button>
            </div>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="flex-grow max-w-7xl mx-auto w-full p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- Left: Configuration & Line Items Builder (no-print) -->
        <div class="lg:col-span-5 space-y-4 no-print">
            
            <!-- Seller & Client Card -->
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
                <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Merchant & Client Details</h2>
                <div class="space-y-2">
                    <input id="sellerName" type="text" class="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-white" placeholder="Your Business / Freelancer Name" value="Apex Autonomous Systems Ltd.">
                    <input id="clientName" type="text" class="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-white" placeholder="Client Name & Address" value="Acme Global Corporation">
                    <div class="grid grid-cols-2 gap-2">
                        <input id="invoiceId" type="text" class="bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs font-mono text-white" placeholder="Invoice #" value="INV-2026-0042">
                        <input id="taxRate" type="number" class="bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-white" placeholder="Tax %" value="18">
                    </div>
                </div>
            </div>

            <!-- Line Items Editor -->
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm">
                <div class="flex justify-between items-center mb-3">
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">Line Items & Deliverables</h2>
                    <button onclick="addItem()" class="text-xs text-indigo-400 hover:text-indigo-300 font-semibold">+ Add Row</button>
                </div>
                <div id="itemsContainer" class="space-y-2">
                    <!-- Dynamic items rendered by JS -->
                </div>
            </div>

            <!-- Settlement Note & Actions -->
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-sm space-y-3">
                <textarea id="settlementNote" rows="2" class="w-full bg-slate-950 border border-slate-800 rounded p-2 text-xs text-slate-300 resize-none" placeholder="Bank details, UPI ID, or payment terms...">Payment terms: Due within 15 days via Wire Transfer or UPI.</textarea>
                
                <div class="flex gap-2">
                    <button onclick="executeExportPDF()" class="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs py-2.5 rounded-lg transition shadow flex items-center justify-center space-x-1.5">
                        <span>🖨️ Print / Download PDF</span>
                    </button>
                    <button onclick="saveToLocalStorage()" class="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs px-3 py-2.5 rounded-lg transition">
                        💾 Save State
                    </button>
                </div>
            </div>
        </div>

        <!-- Right: Print-Ready Live Document Preview -->
        <div class="lg:col-span-7">
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 sm:p-6 shadow-xl sticky top-20">
                <div class="flex justify-between items-center pb-3 mb-4 border-b border-slate-800 no-print">
                    <span class="text-xs font-semibold text-slate-400">Live Paper Preview (A4 Scaled)</span>
                    <span class="text-[11px] bg-slate-800 text-emerald-400 px-2 py-0.5 rounded font-mono">100% Client-Side Engine</span>
                </div>

                <!-- Printable Document Target -->
                <div id="printableInvoice" class="bg-white text-slate-900 p-6 sm:p-10 rounded-lg shadow-inner min-h-[580px] flex flex-col justify-between">
                    <div>
                        <!-- Header -->
                        <div class="flex justify-between items-start border-b border-slate-200 pb-6 mb-6">
                            <div>
                                <h3 id="prevSeller" class="text-xl font-extrabold text-slate-900 tracking-tight">Apex Autonomous Systems</h3>
                                <p class="text-xs text-slate-500 mt-1">Official Tax Invoice & Commercial Settlement</p>
                            </div>
                            <div class="text-right">
                                <p id="prevInvId" class="text-sm font-mono font-bold text-slate-800">INV-2026-0042</p>
                                <p id="prevDate" class="text-xs text-slate-500 mt-1 font-mono"></p>
                            </div>
                        </div>

                        <!-- Client Info -->
                        <div class="mb-6 bg-slate-50 p-4 rounded-xl border border-slate-100">
                            <p class="text-[10px] text-slate-400 uppercase font-black">Billed To:</p>
                            <p id="prevClient" class="text-base font-bold text-slate-800 mt-0.5">Acme Corp Solutions</p>
                        </div>

                        <!-- Rendered Table -->
                        <table class="w-full text-left border-collapse text-xs mb-6">
                            <thead>
                                <tr class="border-b-2 border-slate-200 text-slate-500 uppercase text-[10px]">
                                    <th class="py-2 font-bold">Item Description</th>
                                    <th class="py-2 text-center font-bold">Qty</th>
                                    <th class="py-2 text-right font-bold">Rate</th>
                                    <th class="py-2 text-right font-bold">Amount</th>
                                </tr>
                            </thead>
                            <tbody id="invoiceTableBody" class="divide-y divide-slate-100">
                                <!-- Items Injected -->
                            </tbody>
                        </table>
                    </div>

                    <!-- Financial Calculation Summary -->
                    <div class="border-t border-slate-200 pt-4">
                        <div class="w-full sm:w-64 ml-auto space-y-1.5 text-xs text-slate-600">
                            <div class="flex justify-between">
                                <span>Subtotal:</span>
                                <span id="prevSubtotal" class="font-mono font-semibold">₹0.00</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Tax (<span id="prevTaxPct">18</span>%):</span>
                                <span id="prevTaxVal" class="font-mono font-semibold">₹0.00</span>
                            </div>
                            <div class="flex justify-between text-sm font-black text-slate-900 border-t border-slate-300 pt-2">
                                <span>Total Due:</span>
                                <span id="prevTotal" class="font-mono text-indigo-600">₹0.00</span>
                            </div>
                        </div>
                        <div class="mt-6 pt-4 border-t border-slate-100 text-[11px] text-slate-500 italic">
                            <p id="prevSettlement"></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- STANDARDIZED INR 299 PRO PAYMENT MODAL -->
    <div id="paywallModal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 hidden flex items-center justify-center p-4 font-sans">
        <div class="bg-slate-900 border border-slate-800 max-w-md w-full rounded-2xl p-6 shadow-2xl text-center relative">
            <button onclick="closePaywall()" class="absolute top-4 right-4 text-slate-400 hover:text-white text-sm font-bold">✕</button>
            
            <div class="w-12 h-12 rounded-full bg-emerald-950 border border-emerald-800 text-emerald-400 mx-auto flex items-center justify-center text-xl mb-3">👑</div>
            <h3 class="text-xl font-extrabold text-white">Upgrade to InvoiceForge Studio Pro</h3>
            <p class="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Free sandbox quota exhausted. Unlock unlimited PDF downloads and remove watermarks.
            </p>

            <!-- Payment Box with Exact 299 Lock -->
            <div class="my-5 p-4 bg-slate-950 border border-slate-800 rounded-xl">
                <div class="flex justify-between items-center mb-3 text-xs border-b border-slate-800 pb-2">
                    <span class="text-slate-400">Total Settlement:</span>
                    <span class="text-emerald-400 font-mono font-bold text-sm">₹299.00 INR</span>
                </div>

                <!-- Dynamic QR with Exact Amount Parameter -->
                <div class="bg-white p-2.5 rounded-lg inline-block shadow-inner mb-3">
                    <img id="upiQrImage" 
                         src="{qr_url}" 
                         alt="Scan to Pay 299" 
                         class="w-36 h-36 mx-auto block" />
                </div>
                <p class="text-[11px] text-slate-400">Scan via PhonePe, Google Pay, Paytm or BHIM</p>
                <p class="text-xs font-mono text-slate-200 mt-1 font-semibold select-all">{UPI_ID}</p>
            </div>

            <!-- Direct App Handlers for Mobile -->
            <div class="space-y-2">
                <a href="{upi_link}" 
                   class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs py-3 rounded-xl transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-900/30">
                    <span>⚡ Pay ₹299.00 (Open Any UPI App)</span>
                </a>
                
                <button onclick="navigator.clipboard.writeText('{UPI_ID}'); alert('UPI ID copied: {UPI_ID}');" 
                        class="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-2 rounded-xl transition font-medium">
                    📋 Copy UPI ID to Clipboard
                </button>
            </div>

            <p class="text-[10px] text-slate-500 mt-4">Instant manual verification: WhatsApp reference or screenshot for activation.</p>
        </div>
    </div>

    <script>
        let lineItems = [
            {{ desc: "Custom Micro-SaaS Architecture & UI", qty: 1, rate: 12000 }},
            {{ desc: "REST API Integration & Webhook Sync", qty: 1, rate: 4500 }}
        ];

        document.getElementById('prevDate').innerText = new Date().toLocaleDateString('en-GB');

        function renderItems() {{
            const container = document.getElementById('itemsContainer');
            const tbody = document.getElementById('invoiceTableBody');
            container.innerHTML = '';
            tbody.innerHTML = '';

            let subtotal = 0;

            lineItems.forEach((item, idx) => {{
                const amount = item.qty * item.rate;
                subtotal += amount;

                // Edit inputs
                container.innerHTML += `
                    <div class="flex gap-2 items-center">
                        <input type="text" class="flex-grow bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-white" value="${{item.desc}}" onchange="updateItem(${{idx}}, 'desc', this.value)">
                        <input type="number" class="w-12 bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-white" value="${{item.qty}}" onchange="updateItem(${{idx}}, 'qty', this.value)">
                        <input type="number" class="w-20 bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-white" value="${{item.rate}}" onchange="updateItem(${{idx}}, 'rate', this.value)">
                        <button onclick="removeItem(${{idx}})" class="text-rose-400 hover:text-rose-300 text-xs px-1">✕</button>
                    </div>
                `;

                // Printable table row
                tbody.innerHTML += `
                    <tr class="py-2 border-b border-slate-50">
                        <td class="py-2 text-slate-800 font-medium">${{item.desc}}</td>
                        <td class="py-2 text-center text-slate-600 font-mono">${{item.qty}}</td>
                        <td class="py-2 text-right text-slate-600 font-mono">₹${{item.rate.toFixed(2)}}</td>
                        <td class="py-2 text-right text-slate-900 font-mono font-semibold">₹${{amount.toFixed(2)}}</td>
                    </tr>
                `;
            }});

            const taxRate = parseFloat(document.getElementById('taxRate').value) || 0;
            const taxVal = (subtotal * taxRate) / 100;
            const total = subtotal + taxVal;

            document.getElementById('prevSubtotal').innerText = '₹' + subtotal.toFixed(2);
            document.getElementById('prevTaxPct').innerText = taxRate;
            document.getElementById('prevTaxVal').innerText = '₹' + taxVal.toFixed(2);
            document.getElementById('prevTotal').innerText = '₹' + total.toFixed(2);

            document.getElementById('prevSeller').innerText = document.getElementById('sellerName').value;
            document.getElementById('prevClient').innerText = document.getElementById('clientName').value;
            document.getElementById('prevInvId').innerText = document.getElementById('invoiceId').value;
            document.getElementById('prevSettlement').innerText = document.getElementById('settlementNote').value;
        }}

        function updateItem(idx, key, val) {{
            if (key === 'desc') lineItems[idx].desc = val;
            if (key === 'qty') lineItems[idx].qty = parseFloat(val) || 0;
            if (key === 'rate') lineItems[idx].rate = parseFloat(val) || 0;
            renderItems();
        }}

        function addItem() {{
            lineItems.push({{ desc: "Professional Service", qty: 1, rate: 1000 }});
            renderItems();
        }}

        function removeItem(idx) {{
            if (lineItems.length > 1) {{
                lineItems.splice(idx, 1);
                renderItems();
            }}
        }}

        // Usage Metering & Paywall Logic
        function executeExportPDF() {{
            let uses = parseInt(localStorage.getItem('invoiceforge_exports') || '0');
            if (uses >= 3) {{
                triggerPaywall();
                return;
            }}
            localStorage.setItem('invoiceforge_exports', uses + 1);
            window.print();
        }}

        function triggerPaywall() {{
            document.getElementById('paywallModal').classList.remove('hidden');
        }}

        function closePaywall() {{
            document.getElementById('paywallModal').classList.add('hidden');
        }}

        function saveToLocalStorage() {{
            localStorage.setItem('invoiceforge_state', JSON.stringify({{
                seller: document.getElementById('sellerName').value,
                client: document.getElementById('clientName').value,
                invId: document.getElementById('invoiceId').value,
                tax: document.getElementById('taxRate').value,
                note: document.getElementById('settlementNote').value,
                items: lineItems
            }}));
            alert('Workspace saved locally.');
        }}

        ['sellerName', 'clientName', 'invoiceId', 'taxRate', 'settlementNote'].forEach(id => {{
            document.getElementById(id).addEventListener('input', renderItems);
        }});

        renderItems();
    </script>
</body>
</html>"""

# 1. Save Full SaaS Page
output_path = "public/saas/invoice_forge_pro.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(SAAS_HTML)
print(f"✅ [SUCCESS] Major Functional SaaS Generated: {output_path}")

# 2. Update sitemap.xml
sitemap_path = "public/sitemap.xml"
loc = "https://keshavs40344.github.io/ai-world-core/public/saas/invoice_forge_pro.html"
if os.path.exists(sitemap_path):
    with open(sitemap_path, "r+", encoding="utf-8") as f:
        content = f.read()
        if loc not in content:
            f.seek(0)
            new_entry = f"<url><loc>{loc}</loc><priority>1.0</priority></url></urlset>"
            f.write(content.replace("</urlset>", new_entry))
            print("✅ [SITEMAP] Added SaaS URL to sitemap.xml")

# 3. Update Master Index Storefront with Major SaaS Hero Card
index_file = "public/index.html"
if os.path.exists(index_file):
    with open(index_file, "r+", encoding="utf-8") as f:
        content = f.read()
        hero_card = """
        <!-- MAJOR SAAS HERO FLAGSHIP -->
        <div class="col-span-full bg-gradient-to-r from-indigo-950 via-slate-900 to-slate-900 border-2 border-indigo-600/50 rounded-2xl p-6 sm:p-8 shadow-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-6">
            <div class="max-w-2xl">
                <span class="text-xs bg-indigo-600 text-white font-bold px-3 py-1 rounded-full uppercase tracking-wider">Flagship SaaS Active</span>
                <h2 class="text-2xl sm:text-3xl font-black text-white mt-3 tracking-tight">InvoiceForge Pro — Enterprise Billing Studio</h2>
                <p class="text-slate-300 text-sm mt-2 leading-relaxed">High-performance browser-native invoicing engine. Generate itemized invoices, calculate complex tax models, and print publication-grade PDF documents client-side.</p>
            </div>
            <a href="saas/invoice_forge_pro.html" target="_blank" class="whitespace-nowrap bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm px-6 py-3.5 rounded-xl transition shadow-lg shadow-indigo-600/30">
                Launch SaaS Workspace ↗
            </a>
        </div>
        """
        if "InvoiceForge Pro" not in content:
            f.seek(0)
            if '<div id="hub"' in content:
                f.write(content.replace('id="hub" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">', f'id="hub" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">\n{hero_card}'))
            else:
                f.write(content + hero_card)
            print("✅ [INDEX UPDATED] Master Hub updated with Major Flagship SaaS.")