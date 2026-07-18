# confluence-engine

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

    from confluence_engine import Strategy, Signal, StrategyConfig
    import pandas as pd

    class MyStrategy:
        name = "my-strategy"
        def generate_signal(self, df: pd.DataFrame, config: StrategyConfig) -> Signal:
            last = df.iloc[-1]
            if last["rsi"] < 25:
                return {"signal": "BUY", "reason": "deeply oversold", "score": 0.8,
                        "stop_loss": None, "take_profit": None}
            return {"signal": "HOLD", "reason": "wait", "score": 0.0,
                    "stop_loss": None, "take_profit": None}

Pass an optional `scorer=lambda df, config: 0.0..1.0` to `run_strategy` / `run_backtest`; signals scoring below `config.confidence_threshold` are downgraded to HOLD.

## License

MIT
