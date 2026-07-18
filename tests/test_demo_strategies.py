from confluence_engine.indicators import calculate_indicators
from confluence_engine.config import StrategyConfig
from confluence_engine.strategy import Strategy
from confluence_engine.strategies.breakout import BreakoutDemo
from confluence_engine.strategies.mean_reversion import MeanReversionDemo


def test_demo_strategies_satisfy_protocol_and_return_valid_signal(ohlcv):
    cfg = StrategyConfig()
    df = calculate_indicators(ohlcv, cfg.ema_fast, cfg.ema_slow, cfg.rsi_length)
    for strat in (BreakoutDemo(), MeanReversionDemo()):
        assert isinstance(strat, Strategy)
        sig = strat.generate_signal(df, cfg)
        assert sig["signal"] in {"BUY", "SELL", "HOLD"}
        assert 0.0 <= sig["score"] <= 1.0
