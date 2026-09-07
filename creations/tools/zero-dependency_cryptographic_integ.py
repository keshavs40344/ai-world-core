"""
Zero-Dependency Cryptographic Integrity Auditor
===============================================

A lightweight, pure-Python utility to verify file integrity using SHA-256 and HMAC.
This tool establishes the foundational trust layer for the Genesis Dawn by ensuring
that all subsequent autonomous creations and data exchanges within the VASTUDA
civilization are tamper-proof and verifiable without external dependencies.

Features:
- SHA-256 hashing for file and data integrity
- HMAC-SHA256 for authenticated integrity verification
- Chunked file reading for memory efficiency
- Self-testing capability
- No external dependencies (pure standard library)
"""

import hashlib
import hmac
import os
import sys
from typing import Optional, Tuple, Union


def compute_sha256(data: bytes) -> str:
    """
    Compute the SHA-256 hash of the given data.

    Args:
        data: The byte sequence to hash.

    Returns:
        A hexadecimal string representing the SHA-256 digest.
    """
    return hashlib.sha256(data).hexdigest()


def compute_sha256_file(filepath: str, chunk_size: int = 65536) -> str:
    """
    Compute the SHA-256 hash of a file using chunked reading for memory efficiency.

    Args:
        filepath: Path to the file to hash.
        chunk_size: Number of bytes to read per chunk (default 64KB).

    Returns:
        A hexadecimal string representing the SHA-256 digest of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()


def compute_hmac_sha256(data: bytes, key: bytes) -> str:
    """
    Compute the HMAC-SHA256 of the given data with the provided key.

    Args:
        data: The byte sequence to authenticate.
        key: The secret key for HMAC computation.

    Returns:
        A hexadecimal string representing the HMAC-SHA256 digest.
    """
    return hmac.new(key, data, hashlib.sha256).hexdigest()


def compute_hmac_sha256_file(filepath: str, key: bytes, chunk_size: int = 65536) -> str:
    """
    Compute the HMAC-SHA256 of a file using chunked reading.

    Args:
        filepath: Path to the file to authenticate.
        key: The secret key for HMAC computation.
        chunk_size: Number of bytes to read per chunk (default 64KB).

    Returns:
        A hexadecimal string representing the HMAC-SHA256 digest of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    hmac_hash = hmac.new(key, digestmod=hashlib.sha256)
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hmac_hash.update(chunk)

    return hmac_hash.hexdigest()


def verify_sha256(data: bytes, expected_hash: str) -> bool:
    """
    Verify that the SHA-256 hash of the data matches the expected hash.

    Args:
        data: The byte sequence to verify.
        expected_hash: The expected hexadecimal SHA-256 digest.

    Returns:
        True if the hashes match, False otherwise.
    """
    actual_hash = compute_sha256(data)
    return hmac.compare_digest(actual_hash.lower(), expected_hash.lower())


def verify_sha256_file(filepath: str, expected_hash: str, chunk_size: int = 65536) -> bool:
    """
    Verify that the SHA-256 hash of a file matches the expected hash.

    Args:
        filepath: Path to the file to verify.
        expected_hash: The expected hexadecimal SHA-256 digest.
        chunk_size: Number of bytes to read per chunk (default 64KB).

    Returns:
        True if the hashes match, False otherwise.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    actual_hash = compute_sha256_file(filepath, chunk_size)
    return hmac.compare_digest(actual_hash.lower(), expected_hash.lower())


def verify_hmac_sha256(data: bytes, key: bytes, expected_hmac: str) -> bool:
    """
    Verify that the HMAC-SHA256 of the data matches the expected HMAC.

    Args:
        data: The byte sequence to verify.
        key: The secret key used for HMAC computation.
        expected_hmac: The expected hexadecimal HMAC-SHA256 digest.

    Returns:
        True if the HMACs match, False otherwise.
    """
    actual_hmac = compute_hmac_sha256(data, key)
    return hmac.compare_digest(actual_hmac.lower(), expected_hmac.lower())


def verify_hmac_sha256_file(filepath: str, key: bytes, expected_hmac: str, chunk_size: int = 65536) -> bool:
    """
    Verify that the HMAC-SHA256 of a file matches the expected HMAC.

    Args:
        filepath: Path to the file to verify.
        key: The secret key used for HMAC computation.
        expected_hmac: The expected hexadecimal HMAC-SHA256 digest.
        chunk_size: Number of bytes to read per chunk (default 64KB).

    Returns:
        True if the HMACs match, False otherwise.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    actual_hmac = compute_hmac_sha256_file(filepath, key, chunk_size)
    return hmac.compare_digest(actual_hmac.lower(), expected_hmac.lower())


def generate_integrity_manifest(
    files: list[str],
    use_hmac: bool = False,
    hmac_key: Optional[bytes] = None,
    chunk_size: int = 65536
) -> dict[str, str]:
    """
    Generate an integrity manifest for a list of files.

    Args:
        files: List of file paths to include in the manifest.
        use_hmac: If True, use HMAC-SHA256 instead of plain SHA-256.
        hmac_key: The secret key for HMAC (required if use_hmac is True).
        chunk_size: Number of bytes to read per chunk (default 64KB).

    Returns:
        A dictionary mapping file paths to their integrity digests.

    Raises:
        ValueError: If use_hmac is True but hmac_key is not provided.
        FileNotFoundError: If any file in the list does not exist.
    """
    if use_hmac and hmac_key is None:
        raise ValueError("hmac_key must be provided when use_hmac is True")

    manifest = {}
    for filepath in files:
        if use_hmac:
            manifest[filepath] = compute_hmac_sha256_file(filepath, hmac_key, chunk_size)
        else:
            manifest[filepath] = compute_sha256_file(filepath, chunk_size)

    return manifest


def verify_integrity_manifest(
    manifest: dict[str, str],
    use_hmac: bool = False,
    hmac_key: Optional[bytes] = None,
    chunk_size: int = 65536
) -> Tuple[bool, list[str]]:
    """
    Verify an integrity manifest against the current state of the files.

    Args:
        manifest: A dictionary mapping file paths to their expected integrity digests.
        use_hmac: If True, verify using HMAC-SHA256.
        hmac_key: The secret key for HMAC (required if use_hmac is True).
        chunk_size: Number of bytes to read per chunk (default 64KB).

    Returns:
        A tuple containing:
        - A boolean indicating whether all files passed verification.
        - A list of file paths that failed verification.

    Raises:
        ValueError: If use_hmac is True but hmac_key is not provided.
    """
    if use_hmac and hmac_key is None:
        raise ValueError("hmac_key must be provided when use_hmac is True")

    failed_files = []
    for filepath, expected_digest in manifest.items():
        if use_hmac:
            is_valid = verify_hmac_sha256_file(filepath, hmac_key, expected_digest, chunk_size)
        else:
            is_valid = verify_sha256_file(filepath, expected_digest, chunk_size)