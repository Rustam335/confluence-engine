"""Framework core: run a strategy for the latest bar, or backtest it over history.

Both accept an injected Strategy and an optional Scorer, so proprietary scoring
lives in the *caller*, never here.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .config import StrategyConfig
from .strategy import Scorer, Signal, Strategy


def _hold(reason: str) -> Signal:
    return {"signal": "HOLD", "reason": reason, "score": 0.0,
            "stop_loss": None, "take_profit": None}


def run_strategy(
    df: pd.DataFrame,
    strategy: Strategy,
    config: StrategyConfig | None = None,
    *,
    scorer: Scorer | None = None,
) -> Signal:
    """Compute the latest signal. If a scorer is given and its confidence is below
    `config.confidence_threshold`, the signal is downgraded to HOLD."""
    config = config or StrategyConfig()
    sig = strategy.generate_signal(df, config)
    if sig["signal"] != "HOLD" and scorer is not None:
        confidence = float(scorer(df, config))
        if confidence < config.confidence_threshold:
            return _hold(
                f"{strategy.name} {sig['signal']} vetoed by scorer "
                f"(confidence {confidence:.2f} < {config.confidence_threshold})"
            )
        sig = {**sig, "score": confidence}
    return sig


@dataclass
class BacktestResult:
    trades: list[dict] = field(default_factory=list)
    final_equity: float = 0.0
    return_pct: float = 0.0
    n_trades: int = 0


def run_backtest(
    df: pd.DataFrame,
    strategy: Strategy,
    config: StrategyConfig | None = None,
    *,
    scorer: Scorer | None = None,
    initial_equity: float = 10_000.0,
    fee: float = 0.0,
) -> BacktestResult:
    """Long-flat backtest: expanding-window walk. The signal for bar i is computed
    from bars 0..i (inclusive), and any resulting entry/exit fills at bar i's close
    — there is no execution lag. On BUY (flat) go long at that close; on
    SELL/HOLD-with-open-position, exit at that close. Simplified reference impl.

    Note: a position still open on the final bar is not force-closed, so its
    P&L is excluded from the result."""
    equity = initial_equity
    position_price: float | None = None
    trades: list[dict] = []
    warmup = max(config.ema_slow if config else 50, 50)

    for i in range(warmup, len(df)):
        window = df.iloc[: i + 1]
        sig = run_strategy(window, strategy, config, scorer=scorer)
        price = float(df.iloc[i]["close"])
        if position_price is None and sig["signal"] == "BUY":
            position_price = price * (1 + fee)
        # HOLD while long is treated as an exit too (e.g. a scorer veto unwinds
        # the open position), not just an explicit SELL.
        elif position_price is not None and sig["signal"] in ("SELL", "HOLD"):
            gross = (price * (1 - fee)) - position_price
            pnl = equity * (config.risk_percent / 100.0 if config else 0.01) * (gross / position_price)
            equity += pnl
            trades.append({"entry": position_price, "exit": price, "pnl": pnl})
            position_price = None

    return BacktestResult(
        trades=trades,
        final_equity=equity,
        return_pct=(equity - initial_equity) / initial_equity * 100.0,
        n_trades=len(trades),
    )
