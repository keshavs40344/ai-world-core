# Secure Signed URL Guard

A sovereign, zero-dependency cryptographic signing and verification utility designed to eliminate public URL leaks (e.g. HubSpot recording leaks, AWS media leaks).

## Highlights
- **Cryptographic Integrity**: HMAC-SHA256 URL tokenization.
- **Timing-Attack Resilient**: Constant-time signature comparison using `hmac.compare_digest`.
- **Zero Cost**: Built entirely with Python standard library.