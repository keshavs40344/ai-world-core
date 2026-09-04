"""
vault/vector_store.py
=====================
Central Artifact Vault — ChromaDB vector store interface.

Collections:
  - code_helpers      : Reusable utility functions indexed for retrieval
  - project_docs      : README / docstrings from validated projects
  - failure_archive   : Failed attempt analysis for learning / avoidance
  - taxonomy          : Used internally by TaxonomyEngine (not managed here)

Uses `chromadb.PersistentClient` (ChromaDB ≥0.5 API).
Embedding model: all-MiniLM-L6-v2 (downloaded once, cached locally).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from genesis import config

log = logging.getLogger("vault.vectorstore")


def _get_embedding_function():
    """
    Return the best available embedding function.
    Prefers SentenceTransformer (higher quality) but falls back to
    ChromaDB's built-in DefaultEmbeddingFunction (ONNX, ~40MB, no PyTorch).
    """
    try:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        return SentenceTransformerEmbeddingFunction(model_name=config.EMBEDDING_MODEL)
    except Exception:
        log.info("[VaultStore] sentence-transformers not available — using DefaultEmbeddingFunction (ONNX).")
        return embedding_functions.DefaultEmbeddingFunction()


class VectorStore:
    """
    Thin wrapper around ChromaDB providing collection-level operations
    for the three Genesis vault collections.
    """

    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(path=config.CHROMA_PATH)
        self._emb_fn = _get_embedding_function()
        self._code    = self._open(config.CHROMA_COLLECTION_CODE)
        self._docs    = self._open(config.CHROMA_COLLECTION_DOCS)
        self._failures = self._open(config.CHROMA_COLLECTION_FAILURES)
        log.debug("VectorStore initialised (3 collections).")

    def _open(self, name: str):
        return self._client.get_or_create_collection(
            name=name,
            embedding_function=self._emb_fn,
            metadata={"hnsw:space": "cosine"},
        )

    # -----------------------------------------------------------------------
    # Code helpers
    # -----------------------------------------------------------------------

    def add_helper(
        self,
        code: str,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> str:
        """Index a reusable code snippet. Returns the document ID."""
        doc_id = doc_id or str(uuid.uuid4())
        self._code.upsert(
            documents=[code],
            ids=[doc_id],
            metadatas=[metadata or {}],
        )
        return doc_id

    def search_helpers(self, query: str, n_results: int = 5) -> list[str]:
        """Return the top-n code snippets most relevant to the query."""
        if self._code.count() == 0:
            return []
        results = self._code.query(
            query_texts=[query],
            n_results=min(n_results, self._code.count()),
        )
        return results.get("documents", [[]])[0]

    # -----------------------------------------------------------------------
    # Project indexing (called after a project passes tests)
    # -----------------------------------------------------------------------

    def index_project(self, manifest: dict[str, Any]) -> None:
        """
        Index a validated project's description, goals, and category
        into the project_docs collection for future vault retrieval.
        """
        project_id = manifest.get("project_id", str(uuid.uuid4()))
        doc_text = "\n".join([
            f"Project: {manifest.get('name', '')}",
            f"Category: {manifest.get('category', '')} / {manifest.get('subcategory', '')}",
            f"Description: {manifest.get('description', '')}",
            "Goals: " + "; ".join(manifest.get("goals", [])),
        ])
        self._docs.upsert(
            documents=[doc_text],
            ids=[project_id],
            metadatas=[{
                "name":        manifest.get("name", ""),
                "category":    manifest.get("category", ""),
                "subcategory": manifest.get("subcategory", ""),
                "indexed_at":  datetime.now(timezone.utc).isoformat(),
            }],
        )
        log.info(f"[VaultStore] Indexed project: {manifest.get('name')}")

    def search_projects(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        """Find previously built projects similar to the query."""
        if self._docs.count() == 0:
            return []
        results = self._docs.query(
            query_texts=[query],
            n_results=min(n_results, self._docs.count()),
            include=["documents", "metadatas", "distances"],
        )
        output = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({"document": doc, "metadata": meta, "similarity": 1 - dist / 2})
        return output

    # -----------------------------------------------------------------------
    # Failure archive
    # -----------------------------------------------------------------------

    def archive_failure(
        self,
        project_id: str,
        project_name: str,
        error_summary: str,
        manifest: dict[str, Any],
    ) -> None:
        """Archive a circuit-broken failure for post-mortem analysis."""
        doc_text = (
            f"FAILURE: {project_name}\n"
            f"Category: {manifest.get('category', '')}\n"
            f"Error: {error_summary[:1000]}"
        )
        fail_id = f"fail-{project_id[:8]}-{str(uuid.uuid4())[:8]}"
        self._failures.add(
            documents=[doc_text],
            ids=[fail_id],
            metadatas=[{
                "project_id":   project_id,
                "project_name": project_name,
                "failed_at":    datetime.now(timezone.utc).isoformat(),
            }],
        )
        log.info(f"[VaultStore] Failure archived: {project_name} ({fail_id})")

    def search_failures(self, query: str, n_results: int = 3) -> list[str]:
        """Retrieve similar past failures to inform debugging strategies."""
        if self._failures.count() == 0:
            return []
        results = self._failures.query(
            query_texts=[query],
            n_results=min(n_results, self._failures.count()),
        )
        return results.get("documents", [[]])[0]

    # -----------------------------------------------------------------------
    # Stats
    # -----------------------------------------------------------------------

    def stats(self) -> dict[str, int]:
        return {
            "code_helpers":    self._code.count(),
            "project_docs":    self._docs.count(),
            "failure_archive": self._failures.count(),
        }
