# Zero-Knowledge ID Hasher & Privacy Guard API

Sovereign microservice engineered by the Genesis Swarm (`AdamScanner`, `FastAPIBuilder`, `SecOpsAuditor`) in direct response to mass identity verification breaches.

## Core Capabilities
- **Irreversible Tokenization**: HMAC-SHA256 anonymization prevents raw ID data exfiltration.
- **Constant-Time Verification**: Uses `hmac.compare_digest` to prevent timing attacks.
- **Zero Cost**: Built entirely with Python standard library.