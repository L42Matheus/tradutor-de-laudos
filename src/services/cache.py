"""
Servico de cache para economizar chamadas a API
"""

import hashlib
import time
from abc import ABC, abstractmethod
from typing import Optional, Any
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """Entrada do cache com metadata"""
    value: Any
    created_at: float = field(default_factory=time.time)
    hits: int = 0

    def is_expired(self, ttl_seconds: int) -> bool:
        return (time.time() - self.created_at) > ttl_seconds


class CacheInterface(ABC):
    """Interface para implementacoes de cache (permite trocar para Redis futuramente)"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def stats(self) -> dict:
        pass


class InMemoryCache(CacheInterface):
    """Cache em memoria - para producao com multiplas instancias, usar Redis"""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 100):
        self._cache: dict[str, CacheEntry] = {}
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            return None

        if entry.is_expired(self._ttl):
            self.delete(key)
            self._misses += 1
            return None

        entry.hits += 1
        self._hits += 1
        return entry.value

    def set(self, key: str, value: Any) -> None:
        self._cleanup_expired()

        if len(self._cache) >= self._max_size:
            self._evict_oldest()

        self._cache[key] = CacheEntry(value=value)

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict:
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "ttl_seconds": self._ttl
        }

    def _cleanup_expired(self) -> None:
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired(self._ttl)
        ]
        for key in expired_keys:
            del self._cache[key]

    def _evict_oldest(self) -> None:
        if not self._cache:
            return
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
        del self._cache[oldest_key]


class CacheKeyGenerator:
    """Gera chaves de cache baseadas no conteudo"""

    @staticmethod
    def generate(content: str, tipo: str, categoria: str) -> str:
        key_data = f"{content}:{tipo}:{categoria}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]

    @staticmethod
    def generate_from_image(image_base64: str, tipo: str, categoria: str) -> str:
        image_hash = hashlib.md5(image_base64[:1000].encode()).hexdigest()
        return CacheKeyGenerator.generate(image_hash, tipo, categoria)


# Singleton do cache
_cache_instance: Optional[InMemoryCache] = None


def get_cache() -> InMemoryCache:
    """Retorna instancia singleton do cache"""
    global _cache_instance
    if _cache_instance is None:
        from src.config import CACHE_TTL_SECONDS, CACHE_MAX_SIZE
        _cache_instance = InMemoryCache(
            ttl_seconds=CACHE_TTL_SECONDS,
            max_size=CACHE_MAX_SIZE
        )
    return _cache_instance
