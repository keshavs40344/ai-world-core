# ⚗️ Project Genesis — Autonomous Local-First Software Foundry

> **"From idea to tested code, automatically."**

Project Genesis is a 24/7 autonomous software engineering engine that runs
entirely on your local machine. It discovers high-value software opportunities
from public open-source data, generates complete project scaffolds using a local
LLM, validates them inside Docker containers, and gates production releases
behind your explicit sign-off — all without cloud dependency or recurring API costs.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Genesis-Controller  (APScheduler event loop)                        │
│                                                                      │
│   ┌──────────────┐    project_manifest.json    ┌──────────────────┐ │
│   │    RADAR     │ ──────────────────────────► │    FOUNDRY       │ │
│   │  Controller  │                             │  Controller      │ │
│   │              │                             │                  │ │
│   │ • PyPI scan  │                             │ • AgentFactory   │ │
│   │ • GitHub API │                             │ • TaxonomyEngine │ │
│   │ • HF Spaces  │                             │ • SandboxRunner  │ │
│   │ • GapAuditor │                             │ • TestLoop (≤5)  │ │
│   └──────────────┘                             └────────┬─────────┘ │
│                                                         │           │
│   ┌─────────────────────────────────────────────────────▼─────────┐ │
│   │  Vault  (Git + ChromaDB)                                       │ │
│   │  • code_helpers collection   • project_docs collection         │ │
│   │  • failure_archive           • Git-backed project store        │ │
│   └─────────────────────────────────────────────────────┬─────────┘ │
│                                                         │           │
│   ┌─────────────────────────────────────────────────────▼─────────┐ │
│   │  Governance                                                    │ │
│   │  Tier A: ruff + pytest auto-commit (silent digest)            │ │
│   │  Tier B: release card → Operator sign-off → Git tag          │ │
│   └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Runtime |
| [Ollama](https://ollama.ai) | Latest | Local LLM inference |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Latest | Build sandboxing |
| Git | 2.40+ | Vault version control |

---

## Quick Start

### 1. Clone & set up environment

```powershell
cd C:\Users\HP\Desktop\VASTUDA

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```powershell
# Copy the template and edit your settings
copy .env.example .env
notepad .env
```

Key settings in `.env`:
- `OLLAMA_PRIMARY_MODEL` — which model to use (must be pulled first)
- `CYCLE_INTERVAL_SEC` — how often RADAR runs (default: 3600 = 1 hour)

### 3. Pull your LLM model

```powershell
# Pick one based on your available RAM:
ollama pull mistral:7b      # Recommended — 4 GB VRAM, fast code generation
ollama pull llama3.1:8b     # Best reasoning — 8 GB VRAM
ollama pull phi3:mini       # Ultra-light — 2 GB RAM, good for testing
```

### 4. Start ChromaDB (Docker)

```powershell
docker compose up -d chroma
```

### 5. Build the worker image

```powershell
docker build -f workers/Dockerfile.worker -t genesis-worker:latest workers/
```

### 6. Run a dry-run smoke test

```powershell
python -m genesis.controller --dry-run
```

Expected output:
```
✔ Initialising Project Genesis
  ◆ Bootstrapping SQLite state DB … OK
  ◆ Connecting to ChromaDB vault … OK
━━━ Cycle <id> started ━━━
  [STEP 1] RADAR: scanning … [DRY-RUN] Synthetic manifest: csv_to_json_cli
  [STEP 2] FOUNDRY: … [DRY-RUN] Skipping code generation.
━━━ Cycle <id> finished: SUCCESS ━━━
```

### 7. Start the engine (live mode)

```powershell
python -m genesis.controller
```

### 8. Open the Operator Dashboard

```powershell
streamlit run dashboard/app.py
```

Navigate to `http://localhost:8501`

---

## Directory Structure

```
VASTUDA/
├── genesis/            # Core orchestration engine
│   ├── controller.py   # Main event loop
│   ├── config.py       # All configuration
│   ├── state_db.py     # SQLite task queue & event log
│   └── tests/
├── radar/              # CONTROLLER 1: Market Discovery
│   ├── scanner.py      # Trend signal aggregation
│   ├── gap_auditor.py  # LLM-powered gap analysis
│   ├── manifest_writer.py
│   └── tests/
├── foundry/            # CONTROLLER 2: Code Generation
│   ├── agent_factory.py  # Worker provisioning
│   ├── taxonomy_engine.py # Semantic classification
│   ├── sandbox_runner.py  # Docker execution
│   ├── test_loop.py       # Self-healing loop
│   └── tests/
├── vault/              # Central Artifact Vault
│   ├── git_manager.py
│   ├── vector_store.py
│   └── projects/       # Generated project directories (gitignored)
├── governance/         # Tiered release governance
│   ├── tier_a_validator.py
│   ├── tier_b_gate.py
│   ├── digest_logger.py
│   └── tests/
├── workers/            # Docker worker templates
│   └── Dockerfile.worker
├── dashboard/          # Streamlit operator UI
│   └── app.py
├── release_gate/       # Tier B authorization files
├── manifests/          # RADAR output manifests
├── logs/               # Daily digests & event logs
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── .env.example
```

---

## Governance: Tier A vs Tier B

| | Tier A (Automated) | Tier B (Operator Gate) |
|---|---|---|
| **Trigger** | Every passing build | Public/production release |
| **Validation** | `ruff` + `pytest` both exit 0 | Tier A + Operator sign-off |
| **Result** | Silent Git commit + digest entry | Git annotated tag + deployment |
| **Operator action** | None required | Drop `.AUTHORIZE` or `.REJECT` file |

### Authorizing a Tier B Release

When a project reaches the release gate, a Markdown release card appears in
`release_gate/` and on the dashboard. To authorize:

```powershell
# Create the authorize file (engine polls every 30s)
New-Item "release_gate\<project_id>.AUTHORIZE" -ItemType File

# Or reject and purge:
New-Item "release_gate\<project_id>.REJECT" -ItemType File
```

---

## Running Tests

```powershell
# Full test suite
pytest

# Single package
pytest genesis/tests/ -v
pytest radar/tests/ -v
pytest governance/tests/ -v
```

---

## Configuration Reference

All settings can be overridden in `.env`. Key parameters:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_PRIMARY_MODEL` | `mistral:7b` | Primary inference model |
| `OLLAMA_FALLBACK_MODELS` | `phi3:mini,gemma2:2b` | RAM-pressure fallbacks |
| `CYCLE_INTERVAL_SEC` | `3600` | Seconds between RADAR cycles |
| `CIRCUIT_BREAKER_LIMIT` | `5` | Max test retries before archiving |
| `MAX_CONCURRENT_WORKERS` | `2` | Max parallel Docker workers |
| `TIER_B_TIMEOUT_HOURS` | `72` | Hours before gate auto-expires |
| `MONETIZATION_ENABLED` | `false` | Must be manually activated |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built autonomously by Project Genesis v1.0.0*
