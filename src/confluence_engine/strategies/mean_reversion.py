"""Demo mean-reversion strategy: BUY when RSI is oversold near the lower Bollinger band."""
from __future__ import annotations

import pandas as pd

from ..config import StrategyConfig
from ..strategy import Signal

RSI_OVERSOLD = 30.0


class MeanReversionDemo:
    name = "mean-reversion-demo"

    def generate_signal(self, df: pd.DataFrame, config: StrategyConfig) -> Signal:
        if df.empty:
            return {"signal": "HOLD", "reason": "no data", "score": 0.0,
                    "stop_loss": None, "take_profit": None}
        last = df.iloc[-1]
        rsi = float(last["rsi"])
        close = float(last["close"])
        atr = float(last.get("atr", 0.0) or 0.0)
        lower = float(last["bb_lower"])
        if rsi < RSI_OVERSOLD and close <= lower:
            return {
                "signal": "BUY",
                "reason": f"RSI {rsi:.1f} oversold at/below lower band {lower:.4f}",
                "score": 0.65,
                "stop_loss": close - 1.5 * atr if atr else None,
                "take_profit": float(last["bb_middle"]),
            }
        return {"signal": "HOLD", "reason": f"RSI {rsi:.1f} — no entry", "score": 0.0,
                "stop_loss": None, "take_profit": None}
