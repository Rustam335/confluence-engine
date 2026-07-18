"""Demo breakout strategy: BUY when price closes above the prior Donchian high."""
from __future__ import annotations

import pandas as pd

from ..config import StrategyConfig
from ..strategy import Signal


class BreakoutDemo:
    name = "breakout-demo"

    def generate_signal(self, df: pd.DataFrame, config: StrategyConfig) -> Signal:
        if len(df) < 2:
            return {"signal": "HOLD", "reason": "not enough bars",
                    "score": 0.0, "stop_loss": None, "take_profit": None}
        last, prev = df.iloc[-1], df.iloc[-2]
        atr = float(last.get("atr", 0.0) or 0.0)
        close = float(last["close"])
        prior_high = float(prev["donchian_high"])
        if close > prior_high and last["ema_fast"] > last["ema_slow"]:
            return {
                "signal": "BUY",
                "reason": f"close {close:.4f} broke prior Donchian high {prior_high:.4f}",
                "score": 0.7,
                "stop_loss": close - 1.5 * atr if atr else None,
                "take_profit": close + 3.0 * atr if atr else None,
            }
        return {"signal": "HOLD", "reason": "no breakout", "score": 0.0,
                "stop_loss": None, "take_profit": None}
