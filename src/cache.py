# src/cache.py
"""
Cache system for queries and responses
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class RAGCache:
    """Sistema de caché para queries y respuestas"""
    
    def __init__(self, cache_dir: str = "./data/cache", ttl_days: int = 7):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_days * 24 * 3600
        
        self.responses_dir = self.cache_dir / "responses"
        self.embeddings_dir = self.cache_dir / "embeddings"
        self.responses_dir.mkdir(exist_ok=True)
        self.embeddings_dir.mkdir(exist_ok=True)
    
    def get_response(self, query: str) -> Optional[str]:
        """Obtiene respuesta cacheada"""
        cache_key = self._hash_query(query)
        cache_file = self.responses_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if time.time() - data['timestamp'] > self.ttl_seconds:
                logger.debug(f"Cache expired for query: {query[:50]}...")
                cache_file.unlink()
                return None

            logger.debug(f"✅ Cache hit for query: {query[:50]}...")
            return data['response']

        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def set_response(self, query: str, response: str):
        """Guarda respuesta en cache"""
        cache_key = self._hash_query(query)
        cache_file = self.responses_dir / f"{cache_key}.json"
        
        try:
            data = {
                'query': query,
                'response': response,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.debug(f"💾 Response cached: {query[:50]}...")

        except Exception as e:
            logger.warning(f"Error saving cache: {e}")
    
    def clear_expired(self):
        """Limpia entradas expiradas del cache"""
        logger.info("🧹 Cleaning expired cache...")

        cleared = 0
        current_time = time.time()

        for cache_file in self.responses_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)

                if current_time - data['timestamp'] > self.ttl_seconds:
                    cache_file.unlink()
                    cleared += 1

            except Exception:
                cache_file.unlink()
                cleared += 1

        logger.info(f"✅ {cleared} entries deleted")
    
    def clear_all(self):
        """Limpia todo el cache"""
        logger.info("🧹 Cleaning all cache...")

        for cache_file in self.responses_dir.glob("*.json"):
            cache_file.unlink()

        logger.info("✅ Cache cleared")
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del cache"""
        total_files = len(list(self.responses_dir.glob("*.json")))
        
        total_size = sum(
            f.stat().st_size 
            for f in self.responses_dir.glob("*.json")
        )
        
        return {
            'total_cached_queries': total_files,
            'cache_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }
    
    def _hash_query(self, query: str) -> str:
        """Genera hash para query"""
        return hashlib.md5(query.encode('utf-8')).hexdigest()
