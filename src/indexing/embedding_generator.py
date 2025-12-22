# src/indexing/embedding_generator.py
"""
Generates vector embeddings for text chunks
"""
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generates embeddings for chunks"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"📊 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"✅ Model loaded (dimension: {self.dimension})")
    
    def generate_embeddings(self, chunks: List[Dict], batch_size: int = 32) -> List[Dict]:
        """Generates embeddings for all chunks"""
        logger.info(f"🧮 Generating embeddings for {len(chunks)} chunks...")
        
        texts = []
        for chunk in chunks:
            metadata = chunk['metadata']
            enriched_text = self._create_searchable_text(chunk['content'], metadata)
            texts.append(enriched_text)
        
        embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(
                batch_texts,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            embeddings.extend(batch_embeddings)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding
        
        logger.info("✅ Embeddings generated")
        return chunks
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generates embedding for a query"""
        return self.model.encode(query, convert_to_numpy=True)
    
    def _create_searchable_text(self, content: str, metadata: Dict) -> str:
        """Creates enriched text for better search"""
        prefix_parts = [
            f"Module: {metadata.get('module', 'core')}",
            f"Category: {metadata.get('category', 'general')}",
        ]

        if metadata.get('subsystem'):
            prefix_parts.append(f"Subsystem: {metadata['subsystem']}")

        if metadata.get('tags'):
            prefix_parts.append(f"Tags: {', '.join(metadata['tags'][:5])}")
        
        prefix = '\n'.join(prefix_parts)
        
        return f"{prefix}\n\n{content}"