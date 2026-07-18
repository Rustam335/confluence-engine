"""Map symbol internal → format TradingView (untuk chart widget).

Format TradingView: `EXCHANGE:SYMBOL`
  Crypto Gate         → 'GATEIO:BTCUSDT'
  Forex (Oanda/FX)    → 'OANDA:EURUSD'
  Saham IDX           → 'IDX:BBCA'
  Gold                → 'TVC:GOLD'
"""
from __future__ import annotations


def to_tradingview(symbol: str, market: str) -> str:
    s = symbol.upper().replace("/", "")
    market = market.lower()

    if market in ("spot", "crypto"):
        return f"GATEIO:{s}"
    if market == "forex":
        if s in ("XAUUSD", "GOLD"):
            return "TVC:GOLD"
        return f"OANDA:{s}"
    if market == "idx":
        ticker = symbol.split("/")[0].upper()
        return f"IDX:{ticker}"
    return s
