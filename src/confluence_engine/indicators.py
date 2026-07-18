"""Technical indicators: EMA, RSI, ATR, volume MA, ADX, Bollinger Bands, Donchian."""
from __future__ import annotations

import pandas as pd
import pandas_ta as ta


def calculate_indicators(
    df: pd.DataFrame,
    ema_fast: int = 20,
    ema_slow: int = 50,
    rsi_len: int = 14,
    bb_len: int = 20,
    bb_std: float = 2.0,
    adx_len: int = 14,
    donchian_len: int = 20,
) -> pd.DataFrame:
    """Compute all indicators needed by the hybrid strategy.

    Output columns (in addition to OHLCV):
      ema_fast, ema_slow, rsi, atr, vol_ma  (existing)
      bb_upper, bb_middle, bb_lower, bb_width   (for mean reversion + regime)
      adx                                        (for regime detection)
      donchian_high, donchian_low                (for breakout)
    """
    df = df.copy()
    df["ema_fast"] = ta.ema(df["close"], length=ema_fast)
    df["ema_slow"] = ta.ema(df["close"], length=ema_slow)
    df["rsi"] = ta.rsi(df["close"], length=rsi_len)
    df["atr"] = ta.atr(df["high"], df["low"], df["close"])
    df["vol_ma"] = df["volume"].rolling(20).mean()

    # Bollinger Bands — for mean reversion entry + regime detection
    # Note: pandas-ta column naming can differ between versions (BBL_20_2.0 vs BBL_20_2.0_2.0)
    # — detect by prefix.
    bb = ta.bbands(df["close"], length=bb_len, std=bb_std)
    if bb is not None and len(bb.columns) > 0:
        col_lower = next((c for c in bb.columns if c.startswith("BBL_")), None)
        col_middle = next((c for c in bb.columns if c.startswith("BBM_")), None)
        col_upper = next((c for c in bb.columns if c.startswith("BBU_")), None)
        if col_lower and col_middle and col_upper:
            df["bb_lower"] = bb[col_lower]
            df["bb_middle"] = bb[col_middle]
            df["bb_upper"] = bb[col_upper]
            df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]

    # ADX — for regime detection (trending vs ranging)
    adx = ta.adx(df["high"], df["low"], df["close"], length=adx_len)
    if adx is not None and len(adx.columns) > 0:
        col_adx = next((c for c in adx.columns if c.startswith("ADX_")), None)
        if col_adx:
            df["adx"] = adx[col_adx]

    # Donchian channel — for breakout entry
    df["donchian_high"] = df["high"].rolling(donchian_len).max()
    df["donchian_low"] = df["low"].rolling(donchian_len).min()

    return df
