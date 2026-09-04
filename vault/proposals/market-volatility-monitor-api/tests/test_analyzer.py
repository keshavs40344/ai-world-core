"""AutonomousAuditor test suite for market_volatility_monitor_api."""
import pytest
from src.analyzer import AssetSnapshot, MarketVolatilityAnalyzer, create_sample_payload


@pytest.fixture
def analyzer():
    return MarketVolatilityAnalyzer(anomaly_threshold=3.0)


def test_normal_volatility(analyzer):
    snapshot = AssetSnapshot(
        symbol="ETH",
        price_usd=2500.0,
        change_24h_pct=1.2,
        volume_24h_usd=15000000.0,
    )
    report = analyzer.analyze_snapshot(snapshot, tier="FREE")
    assert report.is_anomaly is False
    assert report.status == "NORMAL"
    assert report.tier == "FREE"


def test_anomaly_threshold_trigger(analyzer):
    snapshot = AssetSnapshot(
        symbol="SOL",
        price_usd=110.0,
        change_24h_pct=4.8,  # > threshold 3.0
        volume_24h_usd=5000000.0,
    )
    report = analyzer.analyze_snapshot(snapshot, tier="PRO")
    assert report.is_anomaly is True
    assert report.status == "HIGH_VOLATILITY_ALERT"
    assert report.tier == "PRO"


def test_stdev_calculation(analyzer):
    # Record multiple price ticks
    analyzer.record_price("BTC", 80000.0)
    analyzer.record_price("BTC", 82000.0)
    analyzer.record_price("BTC", 81000.0)
    vol = analyzer.calculate_volatility("BTC")
    assert vol > 0.0


def test_single_sample_volatility(analyzer):
    analyzer.record_price("NEW", 10.0)
    # With only 1 sample, variance cannot be computed -> returns 0.0
    assert analyzer.calculate_volatility("NEW") == 0.0


def test_payload_service_schema():
    payload = create_sample_payload()
    assert payload["status"] == "HEALTHY"
    assert "PRO" in payload["tiers"]
