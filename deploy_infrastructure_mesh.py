#!/usr/bin/env python3
"""
GENESIS ENTERPRISE INFRASTRUCTURE MESH
Provisions core architectural assets across the entire conglomerate:
- Universal Enterprise Client-Side Runtime Engine (public/assets/genesis_engine.js)
- Global Cyberpunk Design System Primitives (public/assets/genesis_ui.css)
- Zero-Cost Client-Side Telemetry & Event Mesh
- Inter-Agent Event Bus for Micro-Service Compositions
"""

import os
import sys
import json

# UTF-8 Console encoding safety
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DIRS = ["public/assets", "public/schemas", "vault/infrastructure", "db"]
for d in DIRS:
    os.makedirs(d, exist_ok=True)

# 1. CORE CLIENT-SIDE ENGINE (State, Bus, Export & Telemetry)
ENGINE_JS = """/**
 * GENESIS ENTERPRISE CLIENT RUNTIME v2.0
 * Zero-dependency, air-gapped operating primitives for Sovereign Micro-SaaS.
 */
(function(window) {
    'use strict';

    const Genesis = {
        version: "2.0.0",
        build: "2026-TITAN",

        // --- 1. LOCAL WORKSPACE STATE PERSISTENCE ---
        State: {
            save: function(key, data) {
                try {
                    localStorage.setItem(`genesis_${key}`, JSON.stringify(data));
                    return true;
                } catch(e) {
                    console.error("[Genesis.State] Write error:", e);
                    return false;
                }
            },
            load: function(key, fallback = null) {
                try {
                    const item = localStorage.getItem(`genesis_${key}`);
                    return item ? JSON.parse(item) : fallback;
                } catch(e) {
                    console.error("[Genesis.State] Read error:", e);
                    return fallback;
                }
            },
            clear: function(key) {
                localStorage.removeItem(`genesis_${key}`);
            }
        },

        // --- 2. ZERO-LEAK LOCAL TELEMETRY BUFFER ---
        Telemetry: {
            logEvent: function(action, metadata = {}) {
                const logs = Genesis.State.load("telemetry_stream", []);
                logs.push({
                    ts: new Date().toISOString(),
                    act: action,
                    meta: metadata,
                    url: window.location.pathname
                });
                if (logs.length > 50) logs.shift(); // retain rolling 50 items
                Genesis.State.save("telemetry_stream", logs);
            },
            getMetrics: function() {
                return Genesis.State.load("telemetry_stream", []);
            }
        },

        // --- 3. EXPORT AND PRINT ENGINES ---
        IO: {
            download: function(filename, content, mime = "text/plain") {
                const blob = new Blob([content], { type: mime });
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(a.href);
                Genesis.Telemetry.logEvent("file_export", { file: filename });
            },
            copy: function(text, btnElement) {
                navigator.clipboard.writeText(text).then(() => {
                    if (btnElement) {
                        const orig = btnElement.innerHTML;
                        btnElement.innerHTML = "✔ Copied";
                        setTimeout(() => { btnElement.innerHTML = orig; }, 1500);
                    }
                    Genesis.Telemetry.logEvent("clipboard_copy");
                });
            }
        },

        // --- 4. NPCI UNIVERSAL AMOUNT-LOCKED GATEWAY ---
        Payments: {
            invokeUPI: function(amount = "299.00", product = "Sovereign_Pro") {
                const vpa = "";
                const payee = "Keshav";
                const note = encodeURIComponent(`Genesis_${product}_Unlock`);
                const uri = `https://github.com/sponsors/keshavs40344
                Genesis.Telemetry.logEvent("paywall_trigger", { amount: amount, product: product });
                window.location.href = uri;
            }
        },

        // --- 5. INTER-AGENT SHARED BUS ---
        Bus: {
            emit: function(channel, data) {
                window.dispatchEvent(new CustomEvent(`genesis_event_${channel}`, { detail: data }));
            },
            on: function(channel, callback) {
                window.addEventListener(`genesis_event_${channel}`, (e) => callback(e.detail));
            }
        }
    };

    window.Genesis = Genesis;
})(window);
"""

# 2. GLOBAL DESIGN PRIMITIVES & TOKENS (CSS)
DESIGN_CSS = """/* GENESIS DESIGN SYSTEM: CYBERPUNK INDUSTRIAL SPEC */
:root {
    --bg-base: #020617;
    --bg-card: rgba(15, 23, 42, 0.75);
    --border-card: rgba(51, 65, 85, 0.8);
    --border-hover: rgba(99, 102, 241, 0.6);
    --accent-indigo: #6366f1;
    --accent-emerald: #10b981;
}

body {
    background-color: var(--bg-base);
    color: #f8fafc;
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    min-height: 100vh;
}

.genesis-card {
    background: var(--bg-card);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-card);
    border-radius: 1rem;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.genesis-card:hover {
    border-color: var(--border-hover);
    transform: translateY(-2px);
    box-shadow: 0 12px 28px -8px rgba(99, 102, 241, 0.15);
}

.glow-pill {
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.4);
    color: #a5b4fc;
}

/* Custom Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #020617;
}
::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #334155;
}
"""

# 3. ENTERPRISE SCHEMA CATALOG FOR SUB-AGENTS
API_SCHEMAS = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "GenesisUniversalServicePayload",
    "type": "object",
    "properties": {
        "engine_id": {"type": "string"},
        "version": {"type": "string"},
        "client_timestamp": {"type": "string"},
        "input_hash": {"type": "string"},
        "result": {"type": "object"}
    },
    "required": ["engine_id", "version", "result"]
}

def provision():
    print("[INFRA MESH] Injecting Universal Core Runtime...")
    
    # Write Engine JS
    with open("public/assets/genesis_engine.js", "w", encoding="utf-8") as f:
        f.write(ENGINE_JS)
    print("  [OK] Delivered: public/assets/genesis_engine.js")

    # Write Design Tokens CSS
    with open("public/assets/genesis_ui.css", "w", encoding="utf-8") as f:
        f.write(DESIGN_CSS)
    print("  [OK] Delivered: public/assets/genesis_ui.css")

    # Write Shared Schema Spec
    with open("public/schemas/service_payload.json", "w", encoding="utf-8") as f:
        json.dump(API_SCHEMAS, f, indent=2)
    print("  [OK] Delivered: public/schemas/service_payload.json")

    # Write Global Infrastructure Manifest
    manifest = {
        "infrastructure_name": "Genesis Autonomous Mesh",
        "protocol_version": "2.0.0",
        "mesh_capabilities": [
            "localStorage_persistent_workspaces",
            "zero_leak_client_telemetry",
            "air_gapped_json_csv_exporters",
            "hardcoded_npci_prefilled_payments",
            "cross_tool_event_bus"
        ],
        "gateway": {
            "vpa": "",
            "payee": "Keshav",
            "default_lock_amount": "299.00"
        }
    }
    with open("vault/infrastructure/mesh_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("  [OK] Delivered: vault/infrastructure/mesh_manifest.json")

    print("\n[PROVISIONING COMPLETE] All required foundational assets active in environment.")

if __name__ == "__main__":
    provision()
