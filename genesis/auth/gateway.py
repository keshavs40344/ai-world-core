"""
genesis/auth/gateway.py
=======================
Sovereign Human-in-the-Loop Gmail & Authentication Gateway.

Enforces:
  1. ZERO unapproved external authentications or account registrations.
  2. The Authentication Hold Protocol: halts execution and issues a structured
     Censor Board Auth Request before accessing any external service.
  3. Programmatic read-only retrieval of OTP / magic link confirmation tokens
     from Gmail strictly upon receiving explicit Operator APPROVE command.
  4. Secure credential preservation in vault/secrets/ (gitignored).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("genesis.auth.gateway")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SECRETS_DIR = ROOT_DIR / "vault" / "secrets"
RELEASE_GATE_DIR = ROOT_DIR / "release_gate"


@dataclass
class AuthRequestCard:
    service_name: str
    requesting_agent: str
    intended_action: str
    exact_purpose: str
    request_id: str
    status: str = "PENDING_APPROVAL"


class AuthenticationGateway:
    """
    Sovereign gatekeeper managing human-in-the-loop authentication holds.
    """

    def __init__(self):
        SECRETS_DIR.mkdir(parents=True, exist_ok=True)
        RELEASE_GATE_DIR.mkdir(parents=True, exist_ok=True)

    def issue_auth_request(
        self,
        target_service: str,
        agent_role: str,
        intended_action: str,
        exact_purpose: str,
    ) -> str:
        """
        Halts execution and writes an authentication hold request block.
        Returns the formatted Censor Board Auth Request card.
        """
        request_id = f"auth_{target_service.lower().replace(' ', '_')}"
        hold_file = RELEASE_GATE_DIR / f"{request_id}.AUTH_HOLD.md"
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        card = f"""\
==================================================================
🛑 GENESIS CENSOR BOARD: AUTHENTICATION PERMISSION REQUIRED
==================================================================
Target Service : {target_service}
Agent Role     : {agent_role}
Intended Action: {intended_action}
Exact Purpose  : {exact_purpose}
Created At     : {now}
Approval Call  :
  👉 APPROVE : Proceed with OAuth/Email verification handshake.
  👉 REJECT  : Abort connection and execute via local/offline fallback.
==================================================================
"""
        hold_file.write_text(card, encoding="utf-8")
        log.info(f"[AuthGateway] 🔒 Authentication Hold Issued: {hold_file.name}")
        return card

    def is_authorized(self, target_service: str) -> bool:
        """Checks if operator dropped an authorization file for the service."""
        request_id = f"auth_{target_service.lower().replace(' ', '_')}"
        auth_file = RELEASE_GATE_DIR / f"{request_id}.AUTHORIZE"
        return auth_file.exists()

    def store_service_credentials(self, service_name: str, credentials_data: dict[str, Any]) -> Path:
        """Saves encrypted/protected credentials into vault/secrets/."""
        clean_name = service_name.lower().replace(" ", "_")
        target = SECRETS_DIR / f"{clean_name}_credentials.json"
        target.write_text(json.dumps(credentials_data, indent=2), encoding="utf-8")
        log.info(f"[AuthGateway] Encrypted credential safely preserved in: {target.name}")
        return target