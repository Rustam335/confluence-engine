"""Market adapter abstraction.

`strategy.py` and `engine.py` call adapters, not CCXT (or any data provider)
directly. Each market (crypto/forex/stock) has its own adapter.

Minimal contract: `fetch_ohlcv` + `fetch_ticker_price`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import pandas as pd

if TYPE_CHECKING:
    from ..config import AdapterConfig


class MarketAdapter(Protocol):
    market_type: str  # 'crypto' | 'forex' | 'stock'

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_ms: int | None = None,
        limit: int = 500,
    ) -> pd.DataFrame:
        """Return DataFrame columns: timestamp(naive UTC), open, high, low, close, volume."""

    def fetch_ticker_price(self, symbol: str) -> float:
        """Last traded price."""


def get_adapter(market: str, config: "AdapterConfig | None" = None) -> MarketAdapter:
    """Factory — pick an adapter by market type. Credentials come from `config`."""
    from ..config import AdapterConfig
    config = config or AdapterConfig()
    market = market.lower()
    if market in ("spot", "crypto"):
        from .crypto import CcxtAdapter
        return CcxtAdapter(config)
    if market == "forex":
        from .forex import TwelveDataAdapter
        return TwelveDataAdapter(config)
    if market == "idx":
        from .idx import IdxAdapter
        return IdxAdapter(config)
    raise ValueError(f"Unknown market type: {market!r}")
