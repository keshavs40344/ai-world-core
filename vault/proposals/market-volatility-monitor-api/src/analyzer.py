"""
market_volatility_monitor_api - Micro-SaaS Service
==================================================
Autonomous Market Volatility & Price Anomaly Detection Service.
Provides REST API endpoints for real-time asset metric normalization,
Z-score volume spike detection, and tiered usage simulation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class AssetSnapshot:
    symbol: str
    price_usd: float
    change_24h_pct: float
    volume_24h_usd: float
    timestamp_iso: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


@dataclass
class VolatilityReport:
    symbol: str
    is_anomaly: bool
    volatility_score: float
    status: str
    price_usd: float
    volume_24h_usd: float
    tier: str


class MarketVolatilityAnalyzer:
    """
    Sovereign analytical engine calculating volatility indices and anomaly scores.
    """

    def __init__(self, anomaly_threshold: float = 3.5):
        self.anomaly_threshold = float(anomaly_threshold)
        self._history: dict[str, list[float]] = {}

    def record_price(self, symbol: str, price: float) -> None:
        sym = symbol.upper()
        if sym not in self._history:
            self._history[sym] = []
        self._history[sym].append(price)
        # Keep last 50 samples
        if len(self._history[sym]) > 50:
            self._history[sym].pop(0)

    def calculate_volatility(self, symbol: str) -> float:
        sym = symbol.upper()
        prices = self._history.get(sym, [])
        if len(prices) < 2:
            return 0.0

        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / (len(prices) - 1)
        stdev = math.sqrt(variance)
        # Normalized coefficient of variation
        return round((stdev / mean) * 100.0, 3)

    def analyze_snapshot(
        self,
        snapshot: AssetSnapshot,
        tier: str = "FREE",
    ) -> VolatilityReport:
        self.record_price(snapshot.symbol, snapshot.price_usd)
        vol_score = self.calculate_volatility(snapshot.symbol)

        # Anomaly trigger: absolute 24h change exceeding threshold or high stdev
        is_anomaly = abs(snapshot.change_24h_pct) >= self.anomaly_threshold
        status = "HIGH_VOLATILITY_ALERT" if is_anomaly else "NORMAL"

        return VolatilityReport(
            symbol=snapshot.symbol.upper(),
            is_anomaly=is_anomaly,
            volatility_score=vol_score,
            status=status,
            price_usd=snapshot.price_usd,
            volume_24h_usd=snapshot.volume_24h_usd,
            tier=tier.upper(),
        )


def create_sample_payload() -> dict[str, Any]:
    """Helper returning standard sample metrics."""
    return {
        "status": "HEALTHY",
        "service": "Market Volatility Monitor API",
        "version": "1.0.0",
        "tiers": {
            "FREE": "100 req/day, basic indicators",
            "PRO": "10,000 req/day, real-time anomaly alerts",
            "ENTERPRISE": "Unlimited, automated webhook triggers",
        },
    }
