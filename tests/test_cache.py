from confluence_engine._cache import TTLCache


def test_get_returns_none_for_missing_key():
    cache = TTLCache(ttl_seconds=60)
    assert cache.get("missing") is None


def test_set_then_get_returns_the_value():
    cache = TTLCache(ttl_seconds=60)
    cache.set("key", "value")
    assert cache.get("key") == "value"


def test_entry_past_ttl_returns_none():
    clock = {"now": 0.0}
    cache = TTLCache(ttl_seconds=10, time_fn=lambda: clock["now"])
    cache.set("key", "value")
    clock["now"] = 10.0  # exactly at TTL boundary -> expired
    assert cache.get("key") is None


def test_entry_before_ttl_boundary_is_still_valid():
    clock = {"now": 0.0}
    cache = TTLCache(ttl_seconds=10, time_fn=lambda: clock["now"])
    cache.set("key", "value")
    clock["now"] = 9.999
    assert cache.get("key") == "value"


def test_inserting_beyond_max_entries_evicts_oldest_lru():
    cache = TTLCache(ttl_seconds=60, max_entries=3)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    cache.set("d", 4)  # should evict "a" (oldest, never touched)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3
    assert cache.get("d") == 4


def test_recently_touched_key_survives_eviction():
    cache = TTLCache(ttl_seconds=60, max_entries=3)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    cache.get("a")  # touch "a" -> moves to most-recently-used
    cache.set("d", 4)  # should now evict "b" instead of "a"
    assert cache.get("a") == 1
    assert cache.get("b") is None
    assert cache.get("c") == 3
    assert cache.get("d") == 4


def test_len_never_exceeds_max_entries():
    cache = TTLCache(ttl_seconds=60, max_entries=2)
    for i in range(10):
        cache.set(f"key{i}", i)
        assert len(cache) <= 2
    assert len(cache) == 2


def test_max_entries_below_one_raises_value_error():
    import pytest

    with pytest.raises(ValueError):
        TTLCache(ttl_seconds=60, max_entries=0)
