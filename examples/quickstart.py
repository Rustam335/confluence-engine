"""Quickstart: fetch data, run a demo strategy, and backtest it.

Run:  python examples/quickstart.py
"""
from confluence_engine import (
    AdapterConfig, StrategyConfig, BreakoutDemo,
    get_adapter, calculate_indicators, run_strategy, run_backtest,
)


def main() -> None:
    cfg = StrategyConfig()
    adapter = get_adapter("crypto", AdapterConfig(exchange="binance"))
    df = adapter.fetch_ohlcv("BTC/USDT", "1h", limit=300)
    df = calculate_indicators(df, cfg.ema_fast, cfg.ema_slow, cfg.rsi_length)

    strat = BreakoutDemo()
    print("Latest signal:", run_strategy(df, strat, cfg))

    result = run_backtest(df, strat, cfg)
    print(f"Backtest: {result.n_trades} trades, return {result.return_pct:.2f}%")


if __name__ == "__main__":
    main()
