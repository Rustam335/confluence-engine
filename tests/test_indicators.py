from confluence_engine.indicators import calculate_indicators
from confluence_engine.fibonacci import fibonacci_levels
from confluence_engine.regime import detect_regime


def test_calculate_indicators_adds_expected_columns(ohlcv):
    df = calculate_indicators(ohlcv, ema_fast=20, ema_slow=50, rsi_len=14)
    for col in ("ema_fast", "ema_slow", "rsi", "atr", "bb_lower", "bb_upper", "donchian_high"):
        assert col in df.columns
    assert df["rsi"].dropna().between(0, 100).all()


def test_fibonacci_levels_returns_mapping(ohlcv):
    fib = fibonacci_levels(ohlcv, lookback=100)
    assert isinstance(fib, dict) and len(fib) > 0


def test_detect_regime_returns_known_regime(ohlcv):
    df = calculate_indicators(ohlcv, 20, 50, 14)
    info = detect_regime(df)
    assert info["regime"] in {"TREND", "RANGE", "NO_TRADE"}
