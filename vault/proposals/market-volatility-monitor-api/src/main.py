"""CLI and Entrypoint for Market Volatility Monitor API."""
from .analyzer import AssetSnapshot, MarketVolatilityAnalyzer, create_sample_payload


def main() -> None:
    print(create_sample_payload())
    analyzer = MarketVolatilityAnalyzer(anomaly_threshold=3.0)
    sample = AssetSnapshot(
        symbol="BTC",
        price_usd=80839.0,
        change_24h_pct=3.88,
        volume_24h_usd=40792353789.0,
    )
    report = analyzer.analyze_snapshot(sample, tier="PRO")
    print(f"[VolatilityMonitor] Analysis complete for {report.symbol}: {report.status}")


if __name__ == "__main__":
    main()
