import os
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

BUS_DIR = os.path.join("vault", "bus")

class MessageBus:
    """Inter-Agent Structured Message Bus for Swarm Consensus."""
    
    def __init__(self, bus_dir: str = BUS_DIR):
        self.bus_dir = bus_dir
        os.makedirs(self.bus_dir, exist_ok=True)

    def publish(self, sender: str, recipient: str, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        msg_id = f"msg_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
        record = {
            "message_id": msg_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": sender,
            "recipient": recipient,
            "topic": topic,
            "payload": payload
        }
        filepath = os.path.join(self.bus_dir, f"{record['timestamp'].replace(':', '-')}_{sender}_{topic}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
        return record

    def list_messages(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        messages = []
        if not os.path.exists(self.bus_dir):
            return messages
            
        files = sorted(os.listdir(self.bus_dir))
        for filename in files:
            if filename.endswith(".json"):
                path = os.path.join(self.bus_dir, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if topic is None or data.get("topic") == topic:
                            messages.append(data)
                except Exception:
                    pass
        return messages

    def get_latest(self, topic: Optional[str] = None) -> Optional[Dict[str, Any]]:
        msgs = self.list_messages(topic=topic)
        return msgs[-1] if msgs else None
