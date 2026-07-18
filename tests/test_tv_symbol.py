from confluence_engine import to_tradingview


def test_crypto_spot_symbol_maps_to_gateio():
    assert to_tradingview("BTC/USDT", "spot") == "GATEIO:BTCUSDT"


def test_crypto_market_alias_maps_to_gateio():
    assert to_tradingview("BTC/USDT", "crypto") == "GATEIO:BTCUSDT"


def test_forex_symbol_maps_to_oanda():
    assert to_tradingview("EUR/USD", "forex") == "OANDA:EURUSD"


def test_forex_gold_xauusd_maps_to_tvc_gold():
    assert to_tradingview("XAUUSD", "forex") == "TVC:GOLD"


def test_forex_gold_alias_maps_to_tvc_gold():
    assert to_tradingview("GOLD", "forex") == "TVC:GOLD"


def test_idx_symbol_maps_to_idx_exchange():
    assert to_tradingview("BBCA/IDR", "idx") == "IDX:BBCA"


def test_unknown_market_returns_cleaned_symbol():
    assert to_tradingview("BTC/USDT", "unknown") == "BTCUSDT"
