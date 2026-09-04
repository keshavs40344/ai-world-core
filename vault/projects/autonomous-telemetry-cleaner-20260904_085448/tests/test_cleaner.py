import pytest
from src.cleaner import TelemetryCleaner

def test_clean_records():
    cleaner = TelemetryCleaner(drop_nulls=True)
    raw = [
        {"metric": " cpu_load ", "val": 42},
        {"metric": "memory", "val": None},
        "invalid_non_dict"
    ]
    res = cleaner.clean_records(raw)
    assert len(res) == 1
    assert res[0]["metric"] == "cpu_load"
    assert res[0]["val"] == "42"

def test_keep_nulls():
    cleaner = TelemetryCleaner(drop_nulls=False)
    raw = [{"k": "v", "null_k": None}]
    res = cleaner.clean_records(raw)
    assert len(res) == 1
    assert res[0]["null_k"] == "None"
