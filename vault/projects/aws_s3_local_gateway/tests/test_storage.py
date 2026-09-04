"""Rigorous QA test suite for aws_s3_local_gateway."""
import shutil
import tempfile
from pathlib import Path

import pytest
from src.storage import LocalS3Gateway


@pytest.fixture
def temp_gateway():
    temp_dir = Path(tempfile.mkdtemp())
    gateway = LocalS3Gateway(storage_root=temp_dir)
    yield gateway
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_bucket_creation(temp_gateway):
    assert temp_gateway.create_bucket("test-bucket") is True
    assert temp_gateway.create_bucket("test-bucket") is False  # Idempotency check


def test_put_and_get_object(temp_gateway):
    temp_gateway.create_bucket("media")
    body = b"Hello Sovereign Genesis World!"
    put_res = temp_gateway.put_object("media", "docs/hello.txt", body, metadata={"author": "Eve"})

    assert put_res["Size"] == len(body)
    assert "ETag" in put_res
    assert "SHA256" in put_res

    get_res = temp_gateway.get_object("media", "docs/hello.txt")
    assert get_res is not None
    assert get_res["Body"] == body
    assert get_res["Metadata"]["author"] == "Eve"
    assert get_res["Metadata"]["sha256"] == put_res["SHA256"]


def test_list_objects_with_prefix(temp_gateway):
    temp_gateway.create_bucket("data")
    temp_gateway.put_object("data", "logs/2026/01.log", b"log1")
    temp_gateway.put_object("data", "logs/2026/02.log", b"log2")
    temp_gateway.put_object("data", "reports/q1.pdf", b"pdf")

    logs_list = temp_gateway.list_objects_v2("data", prefix="logs/")
    assert logs_list["KeyCount"] == 2
    assert len(logs_list["Contents"]) == 2

    all_list = temp_gateway.list_objects_v2("data")
    assert all_list["KeyCount"] == 3


def test_delete_object(temp_gateway):
    temp_gateway.create_bucket("archive")
    temp_gateway.put_object("archive", "to_delete.txt", b"temporary content")

    assert temp_gateway.get_object("archive", "to_delete.txt") is not None
    assert temp_gateway.delete_object("archive", "to_delete.txt") is True
    assert temp_gateway.get_object("archive", "to_delete.txt") is None
    assert temp_gateway.delete_object("archive", "non_existent.txt") is False


def test_persistence_rehydration():
    temp_dir = Path(tempfile.mkdtemp())
    try:
        gw1 = LocalS3Gateway(storage_root=temp_dir)
        gw1.create_bucket("cold-storage")
        gw1.put_object("cold-storage", "backup.sql", b"SELECT 1;")

        # Second gateway instance pointing to same directory (simulating restart)
        gw2 = LocalS3Gateway(storage_root=temp_dir)
        retrieved = gw2.get_object("cold-storage", "backup.sql")
        assert retrieved is not None
        assert retrieved["Body"] == b"SELECT 1;"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
