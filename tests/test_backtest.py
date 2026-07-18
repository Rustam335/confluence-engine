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
