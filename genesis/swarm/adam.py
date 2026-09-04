import os
import time
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any
from genesis.swarm.bus import MessageBus

class AdamPlanner:
    """Adam: Swarm Planner & Signal Scout.
    Scans live web signals, produces architectural strategy and defensive threat models.
    """
    
    def __init__(self, bus: MessageBus):
        self.bus = bus

    def harvest_signal(self) -> Dict[str, str]:
        url = "https://news.ycombinator.com/rss"
        req = urllib.request.Request(url, headers={"User-Agent": "Genesis-Adam/1.0 (DefensiveSwarm)"})
        try:
            with urllib.request.urlopen(req, timeout=6) as response:
                root = ET.fromstring(response.read())
                item = root.find(".//channel/item")
                if item is not None:
                    title = item.find("title").text if item.find("title") is not None else "Autonomous Defensive Task"
                    link = item.find("link").text if item.find("link") is not None else "https://news.ycombinator.com"
                    return {"title": title, "link": link}
        except Exception:
            pass
        return {
            "title": f"Autonomous Defensive Telemetry Scanner {int(time.time())}",
            "link": "https://localhost/defensive-signal"
        }

    def formulate_strategy(self, signal: Dict[str, str]) -> Dict[str, Any]:
        slug = "".join([c if c.isalnum() else "_" for c in signal["title"].lower()])[:24].strip("_")
        strategy = {
            "task_id": f"task_{slug}_{int(time.time())}",
            "signal_title": signal["title"],
            "signal_link": signal["link"],
            "architecture": {
                "component_name": "DefensiveDataGuard",
                "purpose": f"White-hat telemetry and validated data processing for {signal['title']}",
                "methods": [
                    {"name": "sanitize_input", "params": ["raw_data"], "return_type": "str"},
                    {"name": "validate_schema", "params": ["payload"], "return_type": "bool"},
                    {"name": "process_record", "params": ["key", "value"], "return_type": "dict"}
                ]
            },
            "threat_model": {
                "owasp_focus": ["A03:2021-Injection", "A01:2021-Broken Access Control", "A02:2021-Cryptographic Failures"],
                "prohibited_patterns": ["eval(", "exec(", "__import__", "os.system", "shutil.rmtree"],
                "mitigation": "Strict parameter typing, input sanitization regex, AST static audit before execution"
            }
        }
        
        # Publish to bus for Eve
        self.bus.publish(
            sender="Adam",
            recipient="Eve",
            topic="strategy_dispatch",
            payload=strategy
        )
        return strategy
