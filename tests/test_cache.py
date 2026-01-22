"""
Testes unitarios para o servico de cache
"""

import pytest
import time
from src.services.cache import InMemoryCache, CacheKeyGenerator, CacheEntry


class TestCacheEntry:
    def test_entry_not_expired(self):
        entry = CacheEntry(value="test")
        assert entry.is_expired(ttl_seconds=3600) is False

    def test_entry_expired(self):
        entry = CacheEntry(value="test")
        entry.created_at = time.time() - 7200  # 2 horas atras
        assert entry.is_expired(ttl_seconds=3600) is True


class TestInMemoryCache:
    def test_set_and_get(self):
        cache = InMemoryCache(ttl_seconds=3600)
        cache.set("key1", {"data": "value"})
        result = cache.get("key1")
        assert result == {"data": "value"}

    def test_get_nonexistent_key(self):
        cache = InMemoryCache()
        result = cache.get("nonexistent")
        assert result is None

    def test_delete(self):
        cache = InMemoryCache()
        cache.set("key1", "value")
        cache.delete("key1")
        assert cache.get("key1") is None

    def test_clear(self):
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_max_size_eviction(self):
        cache = InMemoryCache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Deve remover key1
        assert cache.get("key1") is None
        assert cache.get("key3") == "value3"

    def test_stats(self):
        cache = InMemoryCache()
        cache.set("key1", "value")
        cache.get("key1")  # hit
        cache.get("key2")  # miss
        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1


class TestCacheKeyGenerator:
    def test_generate_same_input_same_key(self):
        key1 = CacheKeyGenerator.generate("texto", "tipo1", "laudo")
        key2 = CacheKeyGenerator.generate("texto", "tipo1", "laudo")
        assert key1 == key2

    def test_generate_different_input_different_key(self):
        key1 = CacheKeyGenerator.generate("texto1", "tipo1", "laudo")
        key2 = CacheKeyGenerator.generate("texto2", "tipo1", "laudo")
        assert key1 != key2

    def test_key_length(self):
        key = CacheKeyGenerator.generate("texto", "tipo", "categoria")
        assert len(key) == 32
