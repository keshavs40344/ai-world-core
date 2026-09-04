"""CLI Entrypoint for Unified ReBAC Policy Engine."""
from .engine import UnifiedReBACEngine, create_service_spec


def main() -> None:
    spec = create_service_spec()
    print(f"[{spec['title']}] Initialized v{spec['version']}")
    engine = UnifiedReBACEngine()
    engine.add_relation("user:alice", "owner", "workspace:genesis")
    res = engine.check("user:alice", "delete", "workspace:genesis")
    print(f"Auth check user:alice -> delete -> workspace:genesis : Allowed={res.allowed} ({res.reason})")


if __name__ == "__main__":
    main()
