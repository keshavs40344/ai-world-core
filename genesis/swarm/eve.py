import os
from typing import Dict, Any
from genesis.swarm.bus import MessageBus

class EveDispatcher:
    """Eve: Task Dispatcher & Assembler.
    Ingests Adam's strategy and dispatches parallel tasks to Builder and Defensive Auditor.
    """
    
    def __init__(self, bus: MessageBus):
        self.bus = bus

    def dispatch(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        task_id = strategy["task_id"]
        builder_spec = {
            "task_id": task_id,
            "target_class": strategy["architecture"]["component_name"],
            "methods": strategy["architecture"]["methods"],
            "constraints": strategy["threat_model"]["prohibited_patterns"]
        }
        auditor_spec = {
            "task_id": task_id,
            "owasp_rules": strategy["threat_model"]["owasp_focus"],
            "banned_tokens": strategy["threat_model"]["prohibited_patterns"],
            "required_mitigations": strategy["threat_model"]["mitigation"]
        }
        
        dispatch_package = {
            "task_id": task_id,
            "builder_spec": builder_spec,
            "auditor_spec": auditor_spec
        }
        
        self.bus.publish(
            sender="Eve",
            recipient="SpecialistBuilder",
            topic="builder_dispatch",
            payload=builder_spec
        )
        self.bus.publish(
            sender="Eve",
            recipient="DefensiveAuditor",
            topic="auditor_dispatch",
            payload=auditor_spec
        )
        return dispatch_package
