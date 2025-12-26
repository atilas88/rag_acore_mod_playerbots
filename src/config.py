# src/config.py
"""
RAG system configuration module
"""

from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class ChunkingConfig:
    chunk_size: int = 1000
    overlap: int = 200
    min_chunk_size: int = 100

@dataclass
class EmbeddingConfig:
    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    batch_size: int = 32

@dataclass
class SearchConfig:
    top_k: int = 5
    hybrid_alpha: float = 0.6
    use_reranking: bool = True
    rerank_top_n: int = 10    

@dataclass
class ClaudeConfig:
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4000
    temperature: float = 0.7

@dataclass
class CacheConfig:
    enabled: bool = True
    ttl_days: int = 7
    cache_dir: str = "./data/cache"  

@dataclass
class Config:
    raw_data_path: str = "./data/raw"
    processed_data_path: str = "./data/processed"
    embeddings_path: str = "./data/embeddings"
    
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    claude: ClaudeConfig = field(default_factory=ClaudeConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    log_level: str = "INFO"
    log_file: str = "./logs/rag.log"

    @classmethod
    def from_yaml(cls, path: str) -> 'Config':
        """Load configuration from YAML file"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        config = cls()
        
        if 'chunking' in data:
            config.chunking = ChunkingConfig(**data['chunking'])
        if 'embedding' in data:
            config.embedding = EmbeddingConfig(**data['embedding'])
        if 'search' in data:
            config.search = SearchConfig(**data['search'])
        if 'claude' in data:
            config.claude = ClaudeConfig(**data['claude'])
        if 'cache' in data:
            config.cache = CacheConfig(**data['cache'])
        
        return config      