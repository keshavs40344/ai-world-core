import os
import sys
import json
import time

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

def deploy_to_public():
    os.makedirs("public/tools", exist_ok=True)
    
    # Read latest earnings pulse or telemetry fallback
    pulse_file = "public/live_earnings_pulse.json"
    telemetry_file = "public/live_telemetry.json"
    tool_name = "utility_tool"
    
    if os.path.exists(pulse_file):
        try:
            with open(pulse_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                tool_name = data.get("latest_venture") or data.get("active_venture", "utility_tool")
        except Exception:
            pass
    elif os.path.exists(telemetry_file):
        try:
            with open(telemetry_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                tool_name = data.get("active_venture") or data.get("latest_venture", "utility_tool")
        except Exception:
            pass
            
    # Clean tool name for safe filesystem and URL usage
    tool_slug = "".join([c if c.isalnum() else "_" for c in tool_name]).strip("_")
    
    # Live HTML Web Tool synthesize karta hai direct public access ke liye
    html_tool = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Genesis Tool: {tool_slug}</title>
    <style>
        body {{ background:#0f172a; color:#f8fafc; font-family:sans-serif; padding:2rem; }}
        .box {{ max-width:600px; margin:auto; background:#1e293b; padding:1.5rem; border-radius:8px; border:1px solid #334155; }}
        textarea, input {{ width:100%; padding:0.6rem; margin-top:0.5rem; background:#0b0f19; color:#38bdf8; border:1px solid #475569; border-radius:4px; box-sizing: border-box; }}
        button {{ margin-top:1rem; padding:0.6rem 1.2rem; background:#38bdf8; color:#000; font-weight:bold; border:none; border-radius:4px; cursor:pointer; }}
        button:hover {{ background:#0284c7; }}
        pre {{ background:#030712; padding:1rem; border-radius:4px; overflow-x:auto; margin-top:1rem; }}
    </style>
</head>
<body>
    <div class="box">
        <h2>⚡ Live Autonomous Utility: {tool_slug}</h2>
        <p style="color:#94a3b8;font-size:0.9rem;">De-facto monetization pipeline: Programmatic Traffic & Micro-Services</p>
        <textarea id="inputText" rows="4" placeholder="Enter input data here..."></textarea>
        <button onclick="runTool()">Execute Live</button>
        <pre id="outputResult">Ready for input...</pre>
    </div>
    <script>
        function runTool() {{
            const input = document.getElementById('inputText').value;
            if(!input) return alert("Please enter some text");
            const result = {{
                status: "SUCCESS",
                processed_at: new Date().toISOString(),
                input_length: input.length,
                token_hash: btoa(unescape(encodeURIComponent(input))).slice(0, 16)
            }};
            document.getElementById('outputResult').innerText = JSON.stringify(result, null, 2);
        }}
    </script>
</body>
</html>"""
    
    tool_path = f"public/tools/{tool_slug}.html"
    with open(tool_path, "w", encoding="utf-8") as f:
        f.write(html_tool)

    print(f"✅ Live Web Tool Deployed: {tool_path}")
    return tool_path

if __name__ == "__main__":
    deploy_to_public()
