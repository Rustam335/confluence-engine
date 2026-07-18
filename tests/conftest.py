import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def ohlcv() -> pd.DataFrame:
    """Deterministic 300-bar OHLCV frame (naive UTC timestamps)."""
    n = 300
    rng = np.random.default_rng(42)
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    high = close + rng.uniform(0.1, 1.0, n)
    low = close - rng.uniform(0.1, 1.0, n)
    open_ = close + rng.uniform(-0.5, 0.5, n)
    volume = rng.uniform(1_000, 5_000, n)
    ts = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame(
        {"timestamp": ts, "open": open_, "high": high, "low": low, "close": close, "volume": volume}
    )
