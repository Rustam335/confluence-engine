import pytest

from confluence_engine.adapters import get_adapter
from confluence_engine.config import AdapterConfig


def test_get_adapter_returns_adapter_for_each_market():
    cfg = AdapterConfig(exchange="binance")
    for market in ("crypto", "forex", "idx"):
        adapter = get_adapter(market, cfg)
        assert hasattr(adapter, "fetch_ohlcv")


def test_get_adapter_rejects_unknown_market():
    with pytest.raises(ValueError):
        get_adapter("bogus")
