"""TwelveData adapter — forex data with a generous free tier.

Free tier:
  - 800 req/day, 8 req/min
  - All intervals: 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day, 1week, 1month
  - Up to 5000 candles per call
  - Real-time price via the /price endpoint

Get a free key at https://twelvedata.com/account/api-keys

Symbol format: 'EUR/USD', 'GBP/USD', 'USD/JPY' (slash-separated, same as CCXT).

Live trading is NOT supported — TwelveData is data-only. Live forex trading
needs a broker API (OANDA, MT5, etc.) — deferred to a later phase.
"""
from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pandas as pd
import requests

if TYPE_CHECKING:
    from ..config import AdapterConfig

# TwelveData interval mapping (internal timeframe alias -> TwelveData interval)
_TF_MAP = {
    "1m": "1min", "1min": "1min",
    "5m": "5min", "5min": "5min",
    "15m": "15min", "15min": "15min",
    "30m": "30min", "30min": "30min",
    "45m": "45min", "45min": "45min",
    "1h": "1h",
    "2h": "2h",
    "4h": "4h",
    "1d": "1day", "1day": "1day",
    "1w": "1week", "1week": "1week",
    "1mo": "1month", "1month": "1month",
}

# Cache: (symbol, tf) → (timestamp_loaded, df)
_CACHE: dict[tuple[str, str], tuple[float, pd.DataFrame]] = {}
_CACHE_TTL_SEC = 600  # 10 minutes — saves free-tier quota


class TwelveDataAdapter:
    market_type = "forex"

    def __init__(self, config: "AdapterConfig | None" = None) -> None:
        from ..config import AdapterConfig
        self._config = config or AdapterConfig()
        self._base = "https://api.twelvedata.com"

    def _request(self, path: str, params: dict) -> dict:
        if not self._config.twelvedata_api_key:
            raise RuntimeError(
                "twelvedata_api_key is not set — pass it to AdapterConfig. "
                "Get a free key at https://twelvedata.com/account/api-keys"
            )
        params = {**params, "apikey": self._config.twelvedata_api_key}
        r = requests.get(f"{self._base}/{path}", params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        # TwelveData error: {"code": 401, "message": "...", "status": "error"}
        if isinstance(data, dict) and data.get("status") == "error":
            raise RuntimeError(
                f"TwelveData error ({data.get('code')}): {data.get('message')}"
            )
        return data

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_ms: int | None = None,
        limit: int = 5000,
    ) -> pd.DataFrame:
        cache_key = (symbol, timeframe)
        now = time.time()
        if cache_key in _CACHE:
            cached_at, df_cached = _CACHE[cache_key]
            if now - cached_at < _CACHE_TTL_SEC:
                df = df_cached.copy()
            else:
                df = None
        else:
            df = None

        if df is None:
            interval = _TF_MAP.get(timeframe)
            if not interval:
                raise RuntimeError(f"Timeframe {timeframe!r} is not supported by TwelveData")
            params = {
                "symbol": symbol,
                "interval": interval,
                "outputsize": min(limit, 5000),
                "format": "JSON",
                "order": "ASC",  # ascending — oldest first
            }
            data = self._request("time_series", params)
            values = data.get("values", [])
            if not values:
                raise RuntimeError(
                    f"TwelveData empty values for {symbol} {timeframe}"
                )

            rows = []
            for v in values:
                rows.append({
                    "timestamp": pd.to_datetime(v["datetime"]),
                    "open": float(v["open"]),
                    "high": float(v["high"]),
                    "low": float(v["low"]),
                    "close": float(v["close"]),
                    "volume": float(v.get("volume", 0)),  # forex usually 0
                })
            df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
            _CACHE[cache_key] = (now, df.copy())

        # Filter by since_ms + limit (mimic CCXT semantics)
        if since_ms is not None:
            since_ts = pd.to_datetime(since_ms, unit="ms")
            df = df[df["timestamp"] >= since_ts]
        return df.tail(limit).reset_index(drop=True)

    def fetch_ticker_price(self, symbol: str) -> float:
        data = self._request("price", {"symbol": symbol})
        price = data.get("price")
        if price is None:
            raise RuntimeError(f"TwelveData no price for {symbol}")
        return float(price)

    @property
    def rate_limit_ms(self) -> int:
        # Free tier 8/min = 7.5s between calls. Conservative: 8s.
        return 8_000
