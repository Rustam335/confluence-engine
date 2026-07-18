"""Configuration objects. All values are explicit — the library never reads env."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StrategyConfig:
    ema_fast: int = 20
    ema_slow: int = 50
    rsi_length: int = 14
    fib_lookback: int = 100
    risk_percent: float = 1.0
    confidence_threshold: float = 0.75


@dataclass
class AdapterConfig:
    """Credentials/params passed explicitly to market adapters."""
    exchange: str = "binance"
    exchange_api_key: str = ""
    exchange_api_secret: str = ""
    twelvedata_api_key: str = ""
