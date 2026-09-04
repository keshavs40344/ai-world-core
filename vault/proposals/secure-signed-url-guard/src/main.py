"""CLI Entrypoint for Secure Signed URL Guard."""
from .guard import SecureSignedURLGuard


def main() -> None:
    guard = SecureSignedURLGuard(secret_key="genesis-default-dev-secret")
    url = guard.generate_signed_url("https://api.genesis.local", "recordings/call_123.mp4", ttl_seconds=60)
    print(f"[SecureSignedURLGuard] Generated signed URL:\n{url}")
    ver = guard.verify_signed_url(url)
    print(f"[SecureSignedURLGuard] Verification: {'PASS' if ver.is_valid else 'FAIL'}")

if __name__ == "__main__":
    main()
