"""CCXT adapter — generic crypto exchange (Gate, Binance, Bybit, ...)."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import ccxt
import pandas as pd

if TYPE_CHECKING:
    from ..config import AdapterConfig


class CcxtAdapter:
    market_type = "crypto"

    def __init__(self, config: "AdapterConfig | None" = None) -> None:
        from ..config import AdapterConfig
        self._config = config or AdapterConfig()
        ex_class = getattr(ccxt, self._config.exchange)
        kwargs: dict[str, Any] = {}
        if self._config.exchange_api_key and self._config.exchange_api_secret:
            kwargs["apiKey"] = self._config.exchange_api_key
            kwargs["secret"] = self._config.exchange_api_secret
        self._ex = ex_class(kwargs) if kwargs else ex_class()

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_ms: int | None = None,
        limit: int = 500,
    ) -> pd.DataFrame:
        raw = self._ex.fetch_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=limit)
        df = pd.DataFrame(
            raw, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

    def fetch_ticker_price(self, symbol: str) -> float:
        return float(self._ex.fetch_ticker(symbol)["last"])

    @property
    def rate_limit_ms(self) -> int:
        return getattr(self._ex, "rateLimit", 50) or 50
