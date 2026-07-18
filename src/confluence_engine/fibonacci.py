"""Fibonacci retracement & extension dari swing terakhir."""
from __future__ import annotations

import pandas as pd


def fibonacci_levels(df: pd.DataFrame, lookback: int = 100) -> dict[str, float]:
    recent = df.tail(lookback)
    swing_high = float(recent["high"].max())
    swing_low = float(recent["low"].min())
    diff = swing_high - swing_low

    return {
        "swing_high": swing_high,
        "swing_low": swing_low,
        # Retracement (level di antara swing_low dan swing_high)
        "23.6": swing_high - 0.236 * diff,
        "38.2": swing_high - 0.382 * diff,
        "50.0": swing_high - 0.500 * diff,
        "61.8": swing_high - 0.618 * diff,  # Golden zone
        "78.6": swing_high - 0.786 * diff,
        # LONG extensions — di atas swing_high (untuk TP BUY)
        "tp_127": swing_high + 0.272 * diff,  # TP1 BUY
        "tp_161": swing_high + 0.618 * diff,  # TP2 BUY
        "tp_261": swing_high + 1.618 * diff,  # TP3 BUY
        # SHORT extensions — di bawah swing_low (untuk TP SELL)
        "tp_short_127": swing_low - 0.272 * diff,
        "tp_short_161": swing_low - 0.618 * diff,
        "tp_short_261": swing_low - 1.618 * diff,
    }
