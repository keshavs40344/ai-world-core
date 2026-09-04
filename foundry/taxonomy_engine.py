"""
foundry/taxonomy_engine.py
==========================
FOUNDRY — Semantic project classification via ChromaDB + embeddings.

Instead of a hardcoded category tree, this engine:
  1. Maintains a ChromaDB collection of known category exemplars.
  2. Embeds the incoming manifest's name/description/goals.
  3. Finds the nearest category exemplar by cosine similarity.
  4. If similarity is below a threshold, registers a NEW dynamic category.

This gives the system a self-expanding, embedding-driven namespace.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from genesis import config

log = logging.getLogger("foundry.taxonomy")

# Minimum cosine similarity to match an existing category (0–1)
_SIMILARITY_THRESHOLD = 0.65

# Seed categories — pre-loaded on first init to bootstrap the namespace
_SEED_CATEGORIES: list[dict[str, str]] = [
    {"id": "developer-tools",         "text": "Developer tools, CLI utilities, productivity software for programmers, code formatters, linters, debuggers"},
    {"id": "data-processing",         "text": "Data pipelines, ETL tools, CSV JSON XML processing, data transformation, file conversion"},
    {"id": "performance-monitoring",  "text": "System monitoring, performance profiling, metrics collection, observability, tracing, logging"},
    {"id": "local-ai-ml",             "text": "Local AI inference, machine learning, model serving, vector search, embeddings, NLP"},
    {"id": "automation-scripting",    "text": "Task automation, workflow scripting, cron jobs, scheduled tasks, process automation"},
    {"id": "web-services",            "text": "REST APIs, web servers, FastAPI, Flask, microservices, API gateways"},
    {"id": "security-privacy",        "text": "Encryption, security auditing, privacy tools, secrets management, vulnerability scanning"},
    {"id": "database-tools",          "text": "Database migration, query builder, SQLite tools, schema management, backup utilities"},
    {"id": "content-aggregation",     "text": "RSS feeds, content scrapers, news aggregators, knowledge bases, document indexing"},
    {"id": "desktop-utilities",       "text": "Desktop apps, system tray utilities, file managers, GUI tools, cross-platform desktop"},
]


class TaxonomyEngine:
    """
    Classifies a project manifest into a hierarchical namespace string
    (e.g. 'Developer Tools -> CLI Utilities') using semantic similarity.
    """

    def __init__(self) -> None:
        self._collection = self._init_collection()

    def _init_collection(self):
        """Initialise or open the taxonomy ChromaDB collection."""
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            client = chromadb.PersistentClient(path=config.CHROMA_PATH)

            # Use SentenceTransformer if available, else fall back to ONNX default
            try:
                from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
                emb_fn = SentenceTransformerEmbeddingFunction(model_name=config.EMBEDDING_MODEL)
            except Exception:
                emb_fn = embedding_functions.DefaultEmbeddingFunction()

            collection = client.get_or_create_collection(
                name="taxonomy",
                embedding_function=emb_fn,
                metadata={"hnsw:space": "cosine"},
            )

            # Seed if empty
            if collection.count() == 0:
                log.info("[Taxonomy] Seeding category exemplars …")
                collection.add(
                    documents=[c["text"] for c in _SEED_CATEGORIES],
                    ids=[c["id"] for c in _SEED_CATEGORIES],
                )
                log.info(f"[Taxonomy] {len(_SEED_CATEGORIES)} seed categories loaded.")

            return collection

        except Exception as exc:
            log.warning(f"ChromaDB unavailable — taxonomy will use fallback: {exc}")
            return None

    def classify(self, manifest: dict[str, Any]) -> str:
        """
        Return a namespace string for the manifest.
        Falls back to manifest['category'] / manifest['subcategory'] if
        ChromaDB is unavailable.
        """
        if self._collection is None:
            return f"{manifest.get('category', 'Uncategorized')} -> {manifest.get('subcategory', 'General')}"

        query = " ".join([
            manifest.get("name", ""),
            manifest.get("description", ""),
            " ".join(manifest.get("goals", [])),
            manifest.get("category", ""),
        ])

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=1,
                include=["documents", "distances", "metadatas"],
            )
            distances = results["distances"][0]
            ids = results["ids"][0]

            if not distances:
                return self._register_new(manifest, query)

            # ChromaDB cosine distance: 0 = identical, 2 = opposite
            # Convert to similarity: similarity = 1 - (distance / 2)
            similarity = 1.0 - (distances[0] / 2.0)
            matched_id = ids[0]

            if similarity >= _SIMILARITY_THRESHOLD:
                # Use existing category — prettify the ID
                pretty = matched_id.replace("-", " ").title()
                sub = manifest.get("subcategory", "General")
                log.info(f"[Taxonomy] Classified → '{pretty} -> {sub}' (sim={similarity:.2f})")
                return f"{pretty} -> {sub}"
            else:
                return self._register_new(manifest, query)

        except Exception as exc:
            log.warning(f"[Taxonomy] Classification failed: {exc}")
            return f"{manifest.get('category', 'General')} -> {manifest.get('subcategory', 'General')}"

    def _register_new(self, manifest: dict[str, Any], query: str) -> str:
        """Register a new dynamic category derived from the manifest."""
        category = manifest.get("category", "Uncategorized")
        subcategory = manifest.get("subcategory", "General")
        new_id = f"dynamic-{str(uuid.uuid4())[:8]}"

        try:
            self._collection.add(
                documents=[query],
                ids=[new_id],
                metadatas=[{"category": category, "subcategory": subcategory}],
            )
            log.info(f"[Taxonomy] New category registered: '{category} -> {subcategory}' (id={new_id})")
        except Exception as exc:
            log.warning(f"[Taxonomy] Failed to register new category: {exc}")

        return f"{category} -> {subcategory}"
