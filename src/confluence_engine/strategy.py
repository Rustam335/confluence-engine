"""The plug-in seam: implement `Strategy` to feed signals into the engine."""
from __future__ import annotations

from typing import Callable, Protocol, TypedDict, runtime_checkable

import pandas as pd

from .config import StrategyConfig


class Signal(TypedDict):
    signal: str            # "BUY" | "SELL" | "HOLD"
    reason: str
    score: float
    stop_loss: float | None
    take_profit: float | None


@runtime_checkable
class Strategy(Protocol):
    """Implement this to plug your own logic into run_strategy / run_backtest."""
    name: str

    def generate_signal(self, df: pd.DataFrame, config: StrategyConfig) -> Signal:
        """Given an OHLCV+indicators frame, return the latest Signal."""
        ...


# A scorer maps (frame, config) -> confidence in [0, 1]; injected, never proprietary here.
Scorer = Callable[[pd.DataFrame, StrategyConfig], float]
