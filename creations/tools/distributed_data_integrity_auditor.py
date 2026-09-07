#!/usr/bin/env python3
"""
Distributed Data Integrity Auditor

This script demonstrates a simple distributed data integrity auditor that
continuously verifies cryptographic hashes of critical data across multiple
nodes. Each node runs a lightweight TCP server that returns the hash of a
designated file. A central auditor connects to each node, retrieves the hash,
and compares it against an expected value.

The script is fully self‑contained, uses only the Python standard library,
and includes a self‑testing block that creates temporary files, starts node
servers, runs the auditor, and prints "PASS" if all checks succeed.
"""

import hashlib
import logging
import socket
import socketserver
import threading
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Utility functions
# --------------------------------------------------------------------------- #
def compute_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Compute the cryptographic hash of a file.

    Args:
        file_path: Path to the file to hash.
        algorithm: Hash algorithm to use (default: sha256).

    Returns:
        Hexadecimal hash string.
    """
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


# --------------------------------------------------------------------------- #
# Node server implementation
# --------------------------------------------------------------------------- #
class NodeServer:
    """
    A lightweight TCP server that returns the hash of a designated file.

    The server listens for a single command: "GET_HASH". Upon receiving
    this command, it responds with the precomputed hash of the file.
    """

    def __init__(self, host: str, port: int, file_path: str):
        """
        Initialize the node server.

        Args:
            host: Host address to bind to.
            port: Port number to listen on.
            file_path: Path to the file whose hash will be served.
        """
        self.host = host
        self.port = port
        self.file_path = file_path
        self._hash = compute_hash(file_path)
        self._server: Optional[socketserver.ThreadingTCPServer] = None
        self._thread: Optional[threading.Thread] = None

    # ----------------------------------------------------------------------- #
    # Internal request handler
    # ----------------------------------------------------------------------- #
    class _Handler(socketserver.BaseRequestHandler):
        def handle(self):
            try:
                data = self.request.recv(1024).strip()
                if data == b"GET_HASH":
                    self.request.sendall(self.server._hash.encode() + b"\n")
                else:
                    self.request.sendall(b"UNKNOWN_COMMAND\n")
            except Exception as exc:
                logger.exception("Handler error: %s", exc)

    # ----------------------------------------------------------------------- #
    # Server control methods
    # ----------------------------------------------------------------------- #
    def start(self):
        """Start the TCP server in a background thread."""
        if self._server is not None:
            raise RuntimeError("Server already started")

        self._server = socketserver.ThreadingTCPServer(
            (self.host, self.port), self._Handler
        )
        # Ensure the server can be restarted quickly
        self._server.allow_reuse_address = True

        def serve():
            logger.info("NodeServer starting on %s:%d", self.host, self.port)
            try:
                self._server.serve_forever()
            except Exception as exc:
                logger.exception("Server error: %s", exc)

        self._thread = threading.Thread(target=serve, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the TCP server."""
        if self._server is None:
            return
        logger.info("NodeServer stopping on %s:%d", self.host, self.port)
        self._server.shutdown()
        self._server.server_close()
        self._thread.join()
        self._server = None
        self._thread = None


# --------------------------------------------------------------------------- #
# Auditor implementation
# --------------------------------------------------------------------------- #
def audit_nodes(node_addresses: List[Tuple[str, int]],
                expected_hashes: Dict[Tuple[str, int], str],
                timeout: float = 5.0) -> bool:
    """
    Connect to each node, retrieve its hash, and compare it to the expected value.

    Args:
        node_addresses: List of (host, port) tuples for each node.
        expected_hashes: Mapping from (host, port) to expected hash string.
        timeout: Socket timeout in seconds.

    Returns:
        True if all nodes report the expected hash, False otherwise.
    """
    all_ok = True
    for host, port in node_addresses:
        try:
            with socket.create_connection((host, port), timeout=timeout) as sock:
                sock.sendall(b"GET_HASH\n")
                data = sock.recv(4096).strip()
                received_hash = data.decode()
                expected_hash = expected_hashes.get((host, port))
                if expected_hash is None:
                    logger.warning("No expected hash for %s:%d", host, port)
                    all_ok = False
                    continue
                if received_hash != expected_hash:
                    logger.error(
                        "Hash mismatch on %s:%d: expected %s, got %s",
                        host, port, expected_hash, received_hash,
                    )
                    all_ok = False
                else:
                    logger.info("Hash verified on %s:%d", host, port)
        except Exception as exc:
            logger.exception("Failed to audit %s:%d: %s", host, port, exc)
            all_ok = False
    return all_ok


# --------------------------------------------------------------------------- #
# Self‑testing block
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import tempfile
    import os

    # Create temporary files with known content
    temp_dir = Path(tempfile.mkdtemp())
    file_contents = {
        "node1.txt": b"Hello, world!",
        "node2.txt": b"Python is awesome.",
        "node3.txt": b"Distributed systems are fun.",
    }
    file_paths = {}
    for name, content in file_contents.items():
        path = temp_dir / name
        path.write_bytes(content)
        file_paths[name] = path

    # Compute expected hashes
    expected_hashes: Dict[Tuple[str, int], str] = {}
    node_servers: List[NodeServer] = []

    # Start node servers on localhost with arbitrary free ports
    for idx, (name, path) in enumerate(file_paths.items(), start=1):
        host = "127.0.0.1"
        port = 50000 + idx  # simple port assignment
        server = NodeServer(host, port, str(path))
        server.start()
        node_servers.append(server)
        expected_hashes[(host, port)] = compute_hash(str(path))

    # Give servers a moment to start
    time.sleep(0.5)

    # Run auditor
    try:
        result = audit_nodes(
            node_addresses=list(expected_hashes.keys()),
            expected_hashes=expected_hashes,
        )
        print("PASS" if result else "FAIL")
    finally:
        # Clean up: stop servers and delete temp files
        for server in node_servers:
            server.stop()
        for path in file_paths.values():
            try:
                path.unlink()
            except Exception:
                pass
        try:
            temp_dir.rmdir()
        except Exception:
            pass