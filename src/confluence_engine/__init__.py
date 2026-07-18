"""confluence-engine — a pluggable trading-strategy framework."""
from .config import AdapterConfig, StrategyConfig
from .strategy import Scorer, Signal, Strategy
from .indicators import calculate_indicators
from .fibonacci import fibonacci_levels
from .regime import detect_regime
from .adapters import get_adapter
from .engine import BacktestResult, run_backtest, run_strategy
from .strategies import BreakoutDemo, MeanReversionDemo

__version__ = "0.1.0"

__all__ = [
    "AdapterConfig", "StrategyConfig", "Scorer", "Signal", "Strategy",
    "calculate_indicators", "fibonacci_levels", "detect_regime", "get_adapter",
    "BacktestResult", "run_backtest", "run_strategy",
    "BreakoutDemo", "MeanReversionDemo", "__version__",
]
