from confluence_engine.config import StrategyConfig, AdapterConfig


def test_strategy_config_defaults():
    c = StrategyConfig()
    assert (c.ema_fast, c.ema_slow, c.rsi_length) == (20, 50, 14)
    assert c.confidence_threshold == 0.75


def test_adapter_config_is_explicit_no_env():
    c = AdapterConfig(exchange="gate", exchange_api_key="k", exchange_api_secret="s")
    assert c.exchange == "gate" and c.exchange_api_key == "k"
