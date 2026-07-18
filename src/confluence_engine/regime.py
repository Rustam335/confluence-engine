"""Market regime detector — TREND vs RANGE vs NO_TRADE.

Pakai ADX (kekuatan tren) + Bollinger Band width vs MA20 baseline + EMA bias.

  TREND     : ADX >= 20 AND BB width > MA20 (ekspansi) → arah dari EMA
  RANGE     : ADX < 20 AND BB width <= MA20 (kontraksi/normal)
  NO_TRADE  : ATR ekstrem (volatility spike), atau kondisi campur aduk

Output:
  regime: TREND | RANGE | NO_TRADE
  direction_bias: LONG | SHORT | NEUTRAL  (untuk TREND mode)
  regime_confidence: 0–1 (semakin jauh threshold, semakin tinggi)
"""
from __future__ import annotations

from typing import Literal

import pandas as pd

Regime = Literal["TREND", "RANGE", "NO_TRADE"]
Bias = Literal["LONG", "SHORT", "NEUTRAL"]


def detect_regime(
    df: pd.DataFrame,
    adx_threshold: float = 20.0,
    bb_width_lookback: int = 20,
    atr_extreme_mult: float = 3.0,
) -> dict:
    """Cek candle terakhir terhadap rolling stats."""
    row = df.iloc[-1]
    adx = float(row.get("adx", 0)) if pd.notna(row.get("adx", float("nan"))) else 0.0
    bb_width = float(row["bb_width"]) if "bb_width" in df.columns and pd.notna(row["bb_width"]) else 0.0

    # BB width baseline = MA bb_width 20 candle
    if "bb_width" in df.columns and len(df) >= bb_width_lookback:
        bb_width_ma = float(df["bb_width"].tail(bb_width_lookback).mean())
    else:
        bb_width_ma = bb_width or 1.0

    bb_ratio = bb_width / bb_width_ma if bb_width_ma > 0 else 1.0

    # ATR baseline — deteksi spike (news event)
    atr = float(row.get("atr", 0)) if pd.notna(row.get("atr", float("nan"))) else 0.0
    if "atr" in df.columns and len(df) >= 20:
        atr_ma = float(df["atr"].tail(20).mean())
    else:
        atr_ma = atr or 1.0
    atr_ratio = atr / atr_ma if atr_ma > 0 else 1.0

    # EMA bias
    ema_fast = float(row["ema_fast"]) if pd.notna(row["ema_fast"]) else 0.0
    ema_slow = float(row["ema_slow"]) if pd.notna(row["ema_slow"]) else 0.0
    if ema_fast > ema_slow:
        bias: Bias = "LONG"
    elif ema_fast < ema_slow:
        bias = "SHORT"
    else:
        bias = "NEUTRAL"

    # NO_TRADE: ATR spike → market gila, hindari
    if atr_ratio >= atr_extreme_mult:
        return {
            "regime": "NO_TRADE",
            "direction_bias": "NEUTRAL",
            "regime_confidence": min(1.0, atr_ratio / atr_extreme_mult),
            "adx": round(adx, 2),
            "bb_width": round(bb_width, 5),
            "bb_width_ma": round(bb_width_ma, 5),
            "bb_ratio": round(bb_ratio, 2),
            "atr_ratio": round(atr_ratio, 2),
            "reason": f"ATR ratio {atr_ratio:.2f} > {atr_extreme_mult} (volatility spike)",
        }

    is_trend = adx >= adx_threshold and bb_ratio > 1.0
    is_range = adx < adx_threshold and bb_ratio <= 1.0

    if is_trend:
        regime: Regime = "TREND"
        # Confidence: makin tinggi ADX dan BB ekspansi, makin yakin
        conf = min(1.0, ((adx - adx_threshold) / 20.0) * 0.5 + min(1.0, bb_ratio - 1.0) * 0.5 + 0.5)
    elif is_range:
        regime = "RANGE"
        conf = min(1.0, ((adx_threshold - adx) / adx_threshold) * 0.5 + (1.0 - min(1.0, bb_ratio)) * 0.5 + 0.5)
        bias = "NEUTRAL"  # ranging tidak punya bias arah
    else:
        regime = "NO_TRADE"
        conf = 0.3
        bias = "NEUTRAL"

    return {
        "regime": regime,
        "direction_bias": bias,
        "regime_confidence": round(conf, 2),
        "adx": round(adx, 2),
        "bb_width": round(bb_width, 5),
        "bb_width_ma": round(bb_width_ma, 5),
        "bb_ratio": round(bb_ratio, 2),
        "atr_ratio": round(atr_ratio, 2),
    }
