import pandas as pd
from confluence_engine.strategy import Strategy, Signal
from confluence_engine.config import StrategyConfig


class _Dummy:
    name = "dummy"

    def generate_signal(self, df: pd.DataFrame, config: StrategyConfig) -> Signal:
        return {"signal": "HOLD", "reason": "n/a", "score": 0.0,
                "stop_loss": None, "take_profit": None}


def test_dummy_satisfies_strategy_protocol():
    strat: Strategy = _Dummy()   # structural typing; must not raise at runtime
    sig = strat.generate_signal(pd.DataFrame(), StrategyConfig())
    assert sig["signal"] == "HOLD"
    assert set(sig) == {"signal", "reason", "score", "stop_loss", "take_profit"}
