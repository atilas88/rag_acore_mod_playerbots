# src/indexing/vector_store.py
"""
Stores and searches vectors using FAISS
"""

import faiss
import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    """Advanced store with metadata and filters"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks = []
        self.metadata_index = []
    
    def add_chunks(self, chunks: List[Dict]):
        """Adds chunks with embeddings"""
        logger.info(f"💾 Adding {len(chunks)} chunks to vector store...")
        
        embeddings = np.array([
            chunk['embedding'] for chunk in chunks
        ]).astype('float32')
        
        self.index.add(embeddings)
        
        for chunk in chunks:
            chunk_copy = chunk.copy()
            chunk_copy.pop('embedding', None)
            self.chunks.append(chunk_copy)
            self.metadata_index.append(chunk['metadata'])
        
        logger.info("✅ Chunks added")
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Search with optional filters"""
        
        search_k = k * 3 if filters else k
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, search_k)
        
        results = []
        
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= len(self.chunks):
                continue
            
            chunk = self.chunks[idx]
            metadata = self.metadata_index[idx]
            
            if filters and not self._matches_filters(metadata, filters):
                continue
            
            results.append({
                'chunk': chunk,
                'metadata': metadata,
                'score': float(distance),
                'similarity': 1.0 / (1.0 + float(distance))
            })
            
            if len(results) >= k:
                break
        
        return results
    
    def _matches_filters(self, metadata: Dict, filters: Dict) -> bool:
        """Verifies if metadata matches filters"""
        for key, value in filters.items():
            if key not in metadata:
                continue
            
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            elif isinstance(value, bool):
                if metadata.get(key, False) != value:
                    return False
            else:
                if metadata[key] != value:
                    return False
        
        return True
    
    def save(self, path: str):
        """Saves the vector store"""
        logger.info(f"💾 Saving vector store to: {path}")
        
        Path(path).mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.index, f"{path}/faiss.index")
        
        with open(f"{path}/chunks.pkl", 'wb') as f:
            pickle.dump(self.chunks, f)
        
        with open(f"{path}/metadata.json", 'w', encoding='utf-8') as f:
            json.dump(self.metadata_index, f, indent=2, ensure_ascii=False)
        
        info = {
            'dimension': self.dimension,
            'num_chunks': len(self.chunks),
            'index_type': 'IndexFlatL2'
        }
        with open(f"{path}/info.json", 'w') as f:
            json.dump(info, f, indent=2)
        
        logger.info("✅ Vector store saved")
    
    def load(self, path: str):
        """Loads the vector store"""
        logger.info(f"📂 Loading vector store from: {path}")
        
        self.index = faiss.read_index(f"{path}/faiss.index")
        
        with open(f"{path}/chunks.pkl", 'rb') as f:
            self.chunks = pickle.load(f)
        
        with open(f"{path}/metadata.json", 'r', encoding='utf-8') as f:
            self.metadata_index = json.load(f)
        
        logger.info(f"✅ Vector store loaded ({len(self.chunks)} chunks)")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gets statistics from the store"""
        stats: Dict[str, Any] = {
            'total_chunks': len(self.chunks),
            'dimension': self.dimension,
        }

        categories: Dict[str, int] = {}
        modules: Dict[str, int] = {}
        types: Dict[str, int] = {}
        
        for metadata in self.metadata_index:
            cat = metadata.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
            
            mod = metadata.get('module', 'unknown')
            modules[mod] = modules.get(mod, 0) + 1
            
            typ = metadata.get('type', 'unknown')
            types[typ] = types.get(typ, 0) + 1
        
        stats['by_category'] = categories
        stats['by_module'] = modules
        stats['by_type'] = types
        
        return stats
