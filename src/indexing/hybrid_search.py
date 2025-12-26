# src/indexing/hybrid_search.py
"""
Hybrid search: combines semantic search (embeddings) with BM25 (keywords)
"""
from rank_bm25 import BM25Okapi
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class HybridSearch:
    """Hybrid search: semantic + keywords"""
    
    def __init__(self, vector_store, embedding_generator):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.bm25 = None
        self.tokenized_corpus = None
    
    def build_bm25_index(self):
        """Builds BM25 index for keyword search"""
        logger.info("📊 Building BM25 index...")
        
        corpus = [chunk['content'] for chunk in self.vector_store.chunks]
        self.tokenized_corpus = [doc.lower().split() for doc in corpus]
        
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        logger.info("✅ BM25 index built")
    
    def search(
        self, 
        query: str, 
        k: int = 5, 
        alpha: float = 0.6,
        filters: Dict | None = None
    ) -> List[Dict]:
        """
        Hybrid search

        Args:
            query: User query
            k: Number of results
            alpha: Balance between semantic (1.0) and keywords (0.0)
            filters: Metadata filters
        """
        
        if self.bm25 is None:
            logger.warning("⚠️  BM25 not initialized, using semantic search only")
            return self._semantic_search_only(query, k, filters)

        # Semantic search
        query_embedding = self.embedding_generator.generate_query_embedding(query)
        semantic_results = self.vector_store.search(
            query_embedding, 
            k=k*2,
            filters=filters
        )

        # BM25 search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Combine results
        combined_results = self._combine_results(
            semantic_results,
            bm25_scores,
            alpha,
            filters
        )
        
        return combined_results[:k]

    def _semantic_search_only(self, query: str, k: int, filters: Dict | None) -> List[Dict]:
        """Semantic search only (fallback)"""
        query_embedding = self.embedding_generator.generate_query_embedding(query)
        return self.vector_store.search(query_embedding, k=k, filters=filters)
    
    def _combine_results(
        self,
        semantic_results: List[Dict],
        bm25_scores: np.ndarray,
        alpha: float,
        filters: Dict | None
    ) -> List[Dict]:
        """Combines and re-ranks results"""
        
        semantic_scores_dict = {
            i: result['similarity'] 
            for i, result in enumerate(semantic_results)
        }
        
        if bm25_scores.max() > 0:
            bm25_normalized = bm25_scores / bm25_scores.max()
        else:
            bm25_normalized = bm25_scores
        
        combined_scores = {}
        
        for i, result in enumerate(semantic_results):
            chunk_idx = self._find_chunk_index(result['chunk'])
            if chunk_idx is not None:
                combined_scores[chunk_idx] = {
                    'score': alpha * result['similarity'],
                    'result': result
                }
        
        for idx, bm25_score in enumerate(bm25_normalized):
            if idx in combined_scores:
                combined_scores[idx]['score'] += (1 - alpha) * bm25_score
            else:
                if bm25_score > 0.1:
                    metadata = self.vector_store.metadata_index[idx]
                    if filters and not self.vector_store._matches_filters(metadata, filters):
                        continue
                    
                    combined_scores[idx] = {
                        'score': (1 - alpha) * bm25_score,
                        'result': {
                            'chunk': self.vector_store.chunks[idx],
                            'metadata': metadata,
                            'score': 0,
                            'similarity': 0
                        }
                    }
        
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        final_results = []
        for idx, data in sorted_results:
            result = data['result'].copy()
            result['combined_score'] = data['score']
            final_results.append(result)
        
        return final_results
    
    def _find_chunk_index(self, chunk: Dict) -> int | None:
        """Finds the index of a chunk in the vector store"""
        for i, stored_chunk in enumerate(self.vector_store.chunks):
            if stored_chunk.get('content') == chunk.get('content'):
                return i
        return None
