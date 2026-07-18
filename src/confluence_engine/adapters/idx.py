"""IDX (Indonesia Stock Exchange) adapter via yfinance.

Yahoo Finance supports IDX stocks with the `.JK` suffix:
  BBCA.JK, BBRI.JK, TLKM.JK, ASII.JK, etc.

The standard adapter input format (with a slash) is mapped to Yahoo's:
  'BBCA/IDR' → 'BBCA.JK'
  'BBRI/IDR' → 'BBRI.JK'

Or pass the Yahoo format directly: 'BBCA.JK'.

Free tier:
  - No hard rate limit, but heavy use can trigger a soft block
  - Daily, 1h, 5m, 1m available
  - History: 60 days for 1m, 730 days for 1h, unlimited for 1d
  - Real-time delayed ~15 minutes (acceptable for swing/long-term signals)

Live trading is NOT supported — yfinance is data-only.
Live trading needs an IDX broker API (Mirae/Stockbit — not public),
or the client executes manually after the signal.
"""
from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from ..config import AdapterConfig

# yfinance import time can be slow — defer it
_yf = None


def _yfinance():
    global _yf
    if _yf is None:
        import yfinance as yf
        _yf = yf
    return _yf


_TF_MAP = {
    "1m": "1m", "2m": "2m", "5m": "5m", "15m": "15m", "30m": "30m",
    "60m": "60m", "1h": "60m",
    "1d": "1d", "1day": "1d",
    "1w": "1wk", "1week": "1wk",
    "1mo": "1mo", "1month": "1mo",
}

# Cache: (symbol, tf, period) → (loaded_at, df)
_CACHE: dict[tuple[str, str, str], tuple[float, pd.DataFrame]] = {}
_CACHE_TTL_SEC = 600


def _to_yahoo_symbol(symbol: str) -> str:
    """Normalize: 'BBCA/IDR' or 'BBCA' or 'BBCA.JK' → 'BBCA.JK'."""
    s = symbol.upper().strip()
    if s.endswith(".JK"):
        return s
    if "/" in s:
        s = s.split("/")[0]
    return f"{s}.JK"


class IdxAdapter:
    market_type = "idx"

    def __init__(self, config: "AdapterConfig | None" = None) -> None:
        from ..config import AdapterConfig
        self._config = config or AdapterConfig()

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_ms: int | None = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        yahoo_sym = _to_yahoo_symbol(symbol)
        interval = _TF_MAP.get(timeframe, "1d")

        # yfinance period-based fetch (more reliable than a date-range for intraday)
        # For daily, pull 2 full years; intraday is capped at whatever yfinance allows
        if interval == "1d":
            period = "5y"
        elif interval in ("1wk", "1mo"):
            period = "max"
        elif interval in ("60m", "30m", "15m"):
            period = "60d"  # intraday hourly limit
        else:  # 1m / 5m
            period = "7d"

        cache_key = (yahoo_sym, interval, period)
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
            yf = _yfinance()
            t = yf.Ticker(yahoo_sym)
            raw = t.history(period=period, interval=interval, auto_adjust=True)
            if raw is None or raw.empty:
                raise RuntimeError(
                    f"yfinance returned empty data for {yahoo_sym} interval={interval} period={period}"
                )
            # Normalize columns to the standard adapter format
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(raw.index).tz_localize(None) if raw.index.tz is not None else pd.to_datetime(raw.index),
                "open": raw["Open"].astype(float),
                "high": raw["High"].astype(float),
                "low": raw["Low"].astype(float),
                "close": raw["Close"].astype(float),
                "volume": raw["Volume"].astype(float),
            }).reset_index(drop=True)
            _CACHE[cache_key] = (now, df.copy())

        if since_ms is not None:
            since_ts = pd.to_datetime(since_ms, unit="ms")
            df = df[df["timestamp"] >= since_ts]
        return df.tail(limit).reset_index(drop=True)

    def fetch_ticker_price(self, symbol: str) -> float:
        yahoo_sym = _to_yahoo_symbol(symbol)
        yf = _yfinance()
        t = yf.Ticker(yahoo_sym)
        # fast_info is faster than .info
        try:
            return float(t.fast_info.get("last_price"))
        except Exception:
            # fall back to the latest history bar
            df = self.fetch_ohlcv(symbol, "1d", limit=1)
            return float(df["close"].iloc[-1])

    @property
    def rate_limit_ms(self) -> int:
        return 500  # conservative: 0.5s between calls
