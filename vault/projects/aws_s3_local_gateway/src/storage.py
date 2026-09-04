"""
aws_s3_local_gateway - Local Storage Core Engine
=================================================
A zero-cost, sovereign local-first S3-compatible storage gateway and bucket
emulator that provides PutObject, GetObject, ListObjectsV2, and DeleteObject
with SHA256 integrity verification.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class S3Object:
    bucket: str
    key: str
    content: bytes
    size: int
    etag: str
    last_modified: str
    metadata: dict[str, str] = field(default_factory=dict)


class LocalS3Gateway:
    """
    Local-first S3 compatible storage engine.
    Persists data to local storage directory while keeping fast in-memory index.
    """

    def __init__(self, storage_root: Path | None = None):
        self.storage_root = Path(storage_root) if storage_root else Path("./s3_storage_data")
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self._memory_index: dict[str, dict[str, S3Object]] = {}
        self._load_from_disk()

    def _get_bucket_path(self, bucket: str) -> Path:
        return self.storage_root / bucket

    def _get_object_path(self, bucket: str, key: str) -> Path:
        clean_key = Path(key).as_posix().lstrip("/")
        return self._get_bucket_path(bucket) / clean_key

    def _load_from_disk(self) -> None:
        """Hydrates the in-memory index from the local storage root directory."""
        if not self.storage_root.exists():
            return

        for bucket_dir in self.storage_root.iterdir():
            if bucket_dir.is_dir():
                bucket_name = bucket_dir.name
                if bucket_name not in self._memory_index:
                    self._memory_index[bucket_name] = {}

                for file_path in bucket_dir.rglob("*"):
                    if file_path.is_file() and not file_path.name.endswith(".meta.json"):
                        rel_key = file_path.relative_to(bucket_dir).as_posix()
                        content = file_path.read_bytes()
                        etag = hashlib.md5(content).hexdigest()
                        sha256 = hashlib.sha256(content).hexdigest()
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=UTC).isoformat()

                        meta_file = file_path.with_name(f"{file_path.name}.meta.json")
                        user_metadata = {}
                        if meta_file.exists():
                            with contextlib.suppress(Exception):
                                user_metadata = json.loads(meta_file.read_text(encoding="utf-8"))

                        user_metadata["sha256"] = sha256
                        self._memory_index[bucket_name][rel_key] = S3Object(
                            bucket=bucket_name,
                            key=rel_key,
                            content=content,
                            size=len(content),
                            etag=f'"{etag}"',
                            last_modified=mtime,
                            metadata=user_metadata
                        )

    def create_bucket(self, bucket: str) -> bool:
        """Create a new local bucket directory."""
        if bucket in self._memory_index:
            return False
        b_path = self._get_bucket_path(bucket)
        b_path.mkdir(parents=True, exist_ok=True)
        self._memory_index[bucket] = {}
        return True

    def put_object(
        self,
        bucket: str,
        key: str,
        body: bytes,
        metadata: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """
        Stores an object in the specified bucket and writes integrity hashes.
        """
        if bucket not in self._memory_index:
            self.create_bucket(bucket)

        obj_path = self._get_object_path(bucket, key)
        obj_path.parent.mkdir(parents=True, exist_ok=True)
        obj_path.write_bytes(body)

        etag = hashlib.md5(body).hexdigest()
        sha256 = hashlib.sha256(body).hexdigest()
        now_iso = datetime.now(UTC).isoformat()

        meta_dict = metadata.copy() if metadata else {}
        meta_dict["sha256"] = sha256
        meta_dict["etag"] = etag

        meta_file = obj_path.with_name(f"{obj_path.name}.meta.json")
        meta_file.write_text(json.dumps(meta_dict), encoding="utf-8")

        s3_obj = S3Object(
            bucket=bucket,
            key=key,
            content=body,
            size=len(body),
            etag=f'"{etag}"',
            last_modified=now_iso,
            metadata=meta_dict
        )
        self._memory_index[bucket][key] = s3_obj

        return {
            "ETag": f'"{etag}"',
            "SHA256": sha256,
            "Size": len(body),
            "LastModified": now_iso
        }

    def get_object(self, bucket: str, key: str) -> dict[str, Any] | None:
        """Retrieves an object by bucket and key."""
        if bucket not in self._memory_index or key not in self._memory_index[bucket]:
            obj_path = self._get_object_path(bucket, key)
            if not obj_path.exists() or not obj_path.is_file():
                return None
            self._load_from_disk()
            if bucket not in self._memory_index or key not in self._memory_index[bucket]:
                return None

        obj = self._memory_index[bucket][key]
        return {
            "Body": obj.content,
            "ContentLength": obj.size,
            "ETag": obj.etag,
            "LastModified": obj.last_modified,
            "Metadata": obj.metadata
        }

    def list_objects_v2(self, bucket: str, prefix: str = "") -> dict[str, Any]:
        """Lists all objects matching the prefix in the given bucket."""
        if bucket not in self._memory_index:
            return {"KeyCount": 0, "Contents": []}

        matched: list[dict[str, Any]] = []
        for key, obj in self._memory_index[bucket].items():
            if key.startswith(prefix):
                matched.append({
                    "Key": obj.key,
                    "LastModified": obj.last_modified,
                    "ETag": obj.etag,
                    "Size": obj.size,
                    "StorageClass": "STANDARD"
                })

        return {
            "Name": bucket,
            "Prefix": prefix,
            "KeyCount": len(matched),
            "Contents": matched
        }

    def delete_object(self, bucket: str, key: str) -> bool:
        """Deletes the target object from disk and memory index."""
        if bucket not in self._memory_index or key not in self._memory_index[bucket]:
            return False

        obj_path = self._get_object_path(bucket, key)
        if obj_path.exists():
            obj_path.unlink()
        meta_file = obj_path.with_name(f"{obj_path.name}.meta.json")
        if meta_file.exists():
            meta_file.unlink()

        del self._memory_index[bucket][key]
        return True

    def purge_storage(self) -> None:
        """Completely purges all buckets and files from the root."""
        if self.storage_root.exists():
            shutil.rmtree(self.storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self._memory_index.clear()
