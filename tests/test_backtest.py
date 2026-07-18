import pandas as pd
import pytest

from confluence_engine.indicators import calculate_indicators
from confluence_engine.config import StrategyConfig
from confluence_engine.strategies.breakout import BreakoutDemo
from confluence_engine.engine import run_strategy, run_backtest, BacktestResult


def test_run_strategy_returns_signal(ohlcv):
    cfg = StrategyConfig()
    df = calculate_indicators(ohlcv, cfg.ema_fast, cfg.ema_slow, cfg.rsi_length)
    sig = run_strategy(df, BreakoutDemo(), cfg)
    assert sig["signal"] in {"BUY", "SELL", "HOLD"}


def test_scorer_can_veto_a_signal(ohlcv):
    cfg = StrategyConfig(confidence_threshold=0.75)
    df = calculate_indicators(ohlcv, cfg.ema_fast, cfg.ema_slow, cfg.rsi_length)

    class AlwaysBuy:
        name = "always-buy"
        def generate_signal(self, d, c):
            return {"signal": "BUY", "reason": "x", "score": 1.0,
                    "stop_loss": None, "take_profit": None}

    vetoed = run_strategy(df, AlwaysBuy(), cfg, scorer=lambda d, c: 0.1)
    assert vetoed["signal"] == "HOLD"   # confidence 0.1 < threshold 0.75


def test_run_backtest_returns_result(ohlcv):
    cfg = StrategyConfig()
    df = calculate_indicators(ohlcv, cfg.ema_fast, cfg.ema_slow, cfg.rsi_length)
    result = run_backtest(df, BreakoutDemo(), cfg, initial_equity=10_000.0)
    assert isinstance(result, BacktestResult)
    assert result.final_equity > 0
    assert result.n_trades == len(result.trades)


def test_run_backtest_pnl_scales_by_risk_percent_not_100x():
    """Regression test for the P&L double-conversion bug (Finding 1).

    The old formula included a stray trailing `* 100` that cancelled the
    `risk_percent / 100.0` percent->fraction conversion, so a trade risking
    `risk_percent=1.0` (i.e. 1% of equity) actually moved ~100% of equity.
    This pins the exact expected magnitude: with a single known trade whose
    gross return is `r`, pnl must equal `initial_equity * (risk_percent/100) * r`,
    not `initial_equity * r` (the old, 100x-too-large result).
    """
    n = 60
    entry_price = 100.0
    exit_price = 110.0  # a clear, known 10% upward move
    close = [100.0] * n
    close[50] = entry_price
    close[51] = exit_price
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="h"),
        "open": close,
        "high": [c + 1 for c in close],
        "low": [c - 1 for c in close],
        "close": close,
        "volume": [1_000.0] * n,
    })

    class OneTradeStrategy:
        """Forces exactly one BUY (when flat), then a HOLD that exits it."""
        name = "one-trade-test"

        def generate_signal(self, frame, config):
            n_bars = len(frame)
            if n_bars == 51:
                signal = "BUY"
            elif n_bars == 52:
                signal = "HOLD"  # closes the long opened above
            else:
                signal = "HOLD"  # stays flat everywhere else
            return {"signal": signal, "reason": "test", "score": 1.0,
                    "stop_loss": None, "take_profit": None}

    cfg = StrategyConfig(risk_percent=1.0)
    initial_equity = 10_000.0
    result = run_backtest(df, OneTradeStrategy(), cfg, initial_equity=initial_equity)

    assert result.n_trades == 1
    gross_return = (exit_price - entry_price) / entry_price  # r = 0.10
    expected_pnl = initial_equity * (cfg.risk_percent / 100.0) * gross_return
    old_buggy_pnl = initial_equity * gross_return  # what the pre-fix `* 100` formula gave

    actual_pnl = result.trades[0]["pnl"]
    assert actual_pnl == pytest.approx(expected_pnl, rel=1e-9)
    assert actual_pnl != pytest.approx(old_buggy_pnl, rel=1e-3)
