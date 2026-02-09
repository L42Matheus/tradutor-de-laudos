"""
Testes do serviço de cache
"""
import pytest
import time
from app.services.cache import InMemoryCache, CacheKeyGenerator, CacheEntry


class TestCacheEntry:
    """Testes da classe CacheEntry"""

    def test_entry_creation(self):
        """Testa criação de entrada de cache"""
        entry = CacheEntry(value="test")
        assert entry.value == "test"
        assert entry.hits == 0
        assert entry.created_at > 0

    def test_entry_not_expired(self):
        """Testa que entrada não está expirada"""
        entry = CacheEntry(value="test")
        assert not entry.is_expired(ttl_seconds=3600)

    def test_entry_expired(self):
        """Testa que entrada está expirada"""
        entry = CacheEntry(value="test", created_at=time.time() - 3700)
        assert entry.is_expired(ttl_seconds=3600)


class TestInMemoryCache:
    """Testes da classe InMemoryCache"""

    def test_set_and_get(self):
        """Testa set e get básico"""
        cache = InMemoryCache()
        cache.set("key1", "value1")

        assert cache.get("key1") == "value1"

    def test_get_nonexistent_key(self):
        """Testa get de chave inexistente"""
        cache = InMemoryCache()
        assert cache.get("nonexistent") is None

    def test_delete(self):
        """Testa deleção de chave"""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.delete("key1")

        assert cache.get("key1") is None

    def test_clear(self):
        """Testa limpeza do cache"""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_stats(self):
        """Testa estatísticas do cache"""
        cache = InMemoryCache(max_size=100, ttl_seconds=3600)
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("nonexistent")  # miss

        stats = cache.stats()
        assert stats["size"] == 1
        assert stats["max_size"] == 100
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_max_size_eviction(self):
        """Testa evicção quando atinge tamanho máximo"""
        cache = InMemoryCache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # deve remover key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_ttl_expiration(self):
        """Testa expiração por TTL"""
        cache = InMemoryCache(ttl_seconds=1)
        cache.set("key1", "value1")

        assert cache.get("key1") == "value1"

        time.sleep(1.1)
        assert cache.get("key1") is None


class TestCacheKeyGenerator:
    """Testes da classe CacheKeyGenerator"""

    def test_generate_key(self):
        """Testa geração de chave"""
        key = CacheKeyGenerator.generate("content", "tipo", "categoria")

        assert len(key) == 32
        assert key.isalnum()

    def test_generate_same_key_for_same_input(self):
        """Testa que mesma entrada gera mesma chave"""
        key1 = CacheKeyGenerator.generate("content", "tipo", "categoria")
        key2 = CacheKeyGenerator.generate("content", "tipo", "categoria")

        assert key1 == key2

    def test_generate_different_key_for_different_input(self):
        """Testa que entradas diferentes geram chaves diferentes"""
        key1 = CacheKeyGenerator.generate("content1", "tipo", "categoria")
        key2 = CacheKeyGenerator.generate("content2", "tipo", "categoria")

        assert key1 != key2

    def test_generate_from_image(self):
        """Testa geração de chave a partir de imagem"""
        key = CacheKeyGenerator.generate_from_image("base64data", "tipo", "categoria")

        assert len(key) == 32
        assert key.isalnum()
