"""Market adapter abstraction.

Engine `strategy.py`/`backtest.py`/`executor.py` panggil adapter, bukan CCXT
langsung. Setiap market (crypto/forex/saham) punya adapter sendiri.

Kontrak minimal: `fetch_ohlcv` + `fetch_ticker_price`.
Optional (untuk live trading): `fetch_balance` + `create_market_order`.
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

    def fetch_balance(self, quote: str = "USDT") -> float:
        """Free balance untuk quote asset. Optional — raise NotImplementedError kalau tidak support."""

    def create_market_order(self, symbol: str, side: str, qty: float) -> dict:
        """Place market order. Optional. Return dict info filled price + qty."""


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
