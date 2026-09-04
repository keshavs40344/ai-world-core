"""CLI Entrypoint for Zero-Knowledge ID Hasher."""
from .hasher import ZeroKnowledgeIDHasher, create_api_metadata


def main() -> None:
    meta = create_api_metadata()
    print(f"[{meta['title']}] Initialized")
    hasher = ZeroKnowledgeIDHasher()
    record = hasher.generate_pseudonym("DL-US-987654321", salt="tenant_101")
    print(f"Sample Anonymized Token: {record.pseudonym_id} (Preview: {record.redacted_preview})")


if __name__ == "__main__":
    main()
