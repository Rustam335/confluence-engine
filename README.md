# confluence-engine

[![PyPI version](https://img.shields.io/pypi/v/confluence-engine.svg)](https://pypi.org/project/confluence-engine/)
[![Python versions](https://img.shields.io/pypi/pyversions/confluence-engine.svg)](https://pypi.org/project/confluence-engine/)
[![License: MIT](https://img.shields.io/pypi/l/confluence-engine.svg)](https://github.com/Rustam335/confluence-engine/blob/main/LICENSE)
[![CI](https://github.com/Rustam335/confluence-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/Rustam335/confluence-engine/actions/workflows/ci.yml)

A pluggable trading-strategy framework for Python: technical indicators, market-data adapters (crypto/forex/idx), a backtester, and a clean `Strategy` interface you implement yourself. Bring your own signal logic and scoring — the framework stays out of your way.

## Install

    pip install confluence-engine

## Quickstart

    from confluence_engine import (
        AdapterConfig, StrategyConfig, BreakoutDemo,
        get_adapter, calculate_indicators, run_backtest,
    )

    cfg = StrategyConfig()
    df = get_adapter("crypto", AdapterConfig(exchange="binance")).fetch_ohlcv("BTC/USDT", "1h", limit=300)
    df = calculate_indicators(df, cfg.ema_fast, cfg.ema_slow, cfg.rsi_length)
    print(run_backtest(df, BreakoutDemo(), cfg))

## Write your own strategy

A strategy is any object with a `name` and a `generate_signal(df, config) -> Signal` method.
The `df` you receive already has indicator columns computed (`ema_fast`, `ema_slow`, `rsi`,
`atr`, `adx`, `bb_lower`/`bb_middle`/`bb_upper`, `donchian_high`/`donchian_low`, ...). A
`Signal` is a dict with `signal` (`"BUY"` / `"SELL"` / `"HOLD"`), `reason`, `score`,
`stop_loss`, and `take_profit`.

Here's a complete custom strategy — buy pullbacks inside an uptrend, with ATR-based
stop-loss and take-profit — run end to end through the backtester:

    import pandas as pd
    from confluence_engine import (
        Signal, StrategyConfig, AdapterConfig,
        get_adapter, calculate_indicators, run_backtest,
    )

    class EmaRsiPullback:
        """Buy pullbacks in an uptrend: fast EMA above slow EMA, RSI dipping then recovering."""
        name = "ema-rsi-pullback"

        def generate_signal(self, df: pd.DataFrame, config: StrategyConfig) -> Signal:
            last = df.iloc[-1]
            close, atr = float(last["close"]), float(last["atr"])
            uptrend = last["ema_fast"] > last["ema_slow"]
            pullback = 35 < last["rsi"] < 50  # not oversold — coming back up

            if uptrend and pullback:
                return {
                    "signal": "BUY",
                    "reason": f"uptrend pullback (RSI {last['rsi']:.1f})",
                    "score": 0.7,
                    "stop_loss": close - 2 * atr,
                    "take_profit": close + 3 * atr,
                }
            return {"signal": "HOLD", "reason": "no setup", "score": 0.0,
                    "stop_loss": None, "take_profit": None}

    cfg = StrategyConfig(confidence_threshold=0.5)
    df = get_adapter("crypto", AdapterConfig(exchange="binance")).fetch_ohlcv("ETH/USDT", "1h", limit=500)
    df = calculate_indicators(df, cfg.ema_fast, cfg.ema_slow, cfg.rsi_length)

    result = run_backtest(df, EmaRsiPullback(), cfg)
    print(f"{result.n_trades} trades, return {result.return_pct:.2f}%")

### Bring your own scorer (optional)

A scorer is a `callable(df, config) -> float` returning a confidence in `[0, 1]`. Pass it
to `run_strategy` / `run_backtest`, and any `BUY`/`SELL` scoring below
`config.confidence_threshold` is automatically downgraded to `HOLD` — a clean seam for
plugging in your own conviction model without touching the strategy:

    def trend_strength_scorer(df: pd.DataFrame, config: StrategyConfig) -> float:
        adx = float(df.iloc[-1]["adx"])   # strong trend (ADX >= 40) => full confidence
        return min(adx / 40.0, 1.0)

    result = run_backtest(df, EmaRsiPullback(), cfg, scorer=trend_strength_scorer)

## License

MIT
