def test_public_api_exports():
    import confluence_engine as ce
    for name in ("StrategyConfig", "AdapterConfig", "Strategy", "Signal",
                 "run_strategy", "run_backtest", "BacktestResult",
                 "calculate_indicators", "get_adapter",
                 "BreakoutDemo", "MeanReversionDemo"):
        assert hasattr(ce, name), f"missing export: {name}"
