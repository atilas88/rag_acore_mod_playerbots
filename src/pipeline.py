# src/pipeline.py
"""
Main pipeline for the RAG system
Integrates all components: preprocessing, indexing, retrieval, generation
"""

import os
import time
from typing import List, Dict, Optional, Generator, Union
import logging

from src.config import Config
from src.preprocessing.document_loader import DocumentLoader
from src.indexing.embedding_generator import EmbeddingGenerator
from src.indexing.vector_store import VectorStore
from src.indexing.hybrid_search import HybridSearch
from src.generation.claude_client import ClaudeClient
from src.generation.prompt_builder import PromptBuilder
from src.cache import RAGCache
from src.monitor import RAGMonitor

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Complete RAG pipeline"""

    def __init__(self, config: Config, api_key: str):
        self.config = config

        # Components
        self.document_loader = DocumentLoader(config)
        self.embedding_generator = EmbeddingGenerator(config.embedding.model_name)
        self.vector_store = VectorStore(dimension=config.embedding.dimension)
        self.hybrid_search = None
        self.claude_client = ClaudeClient(api_key=api_key, model=config.claude.model)
        self.prompt_builder = PromptBuilder()

        # Utilities
        if config.cache.enabled:
            self.cache = RAGCache(
                cache_dir=config.cache.cache_dir,
                ttl_days=config.cache.ttl_days
            )
        else:
            self.cache = None

        self.monitor = RAGMonitor()

        logger.info("✅ RAGPipeline initialized")
    
    def build_index(self, force_rebuild: bool = False):
        """Builds the complete index from scratch"""

        logger.info("🏗️  BUILDING RAG INDEX")
        logger.info("="*70)

        start_time = time.time()

        # 1. Load documents
        logger.info("STEP 1: Loading documents...")
        documents = self.document_loader.load_documents(self.config.raw_data_path)

        if not documents:
            logger.error("❌ No documents found")
            return False

        # 2. Process into chunks
        logger.info("STEP 2: Processing documents into chunks...")
        chunks = self.document_loader.process_documents(documents)

        if not chunks:
            logger.error("❌ No chunks generated")
            return False

        # 3. Generate embeddings
        logger.info("STEP 3: Generating embeddings...")
        chunks_with_embeddings = self.embedding_generator.generate_embeddings(
            chunks,
            batch_size=self.config.embedding.batch_size
        )

        # 4. Add to vector store
        logger.info("STEP 4: Building vector store...")
        self.vector_store.add_chunks(chunks_with_embeddings)

        # 5. Build BM25 index
        logger.info("STEP 5: Building BM25 index...")
        self.hybrid_search = HybridSearch(self.vector_store, self.embedding_generator)
        self.hybrid_search.build_bm25_index()

        # 6. Save index
        logger.info("STEP 6: Saving index...")
        self.vector_store.save(self.config.embeddings_path)

        # Save BM25
        import pickle
        bm25_path = os.path.join(self.config.embeddings_path, "bm25.pkl")
        with open(bm25_path, 'wb') as f:
            pickle.dump({
                'bm25': self.hybrid_search.bm25,
                'tokenized_corpus': self.hybrid_search.tokenized_corpus
            }, f)

        elapsed = time.time() - start_time

        # Statistics
        stats = self.vector_store.get_statistics()

        logger.info("="*70)
        logger.info("✅ INDEX BUILT SUCCESSFULLY")
        logger.info(f"⏱️  Total time: {elapsed:.2f} seconds")
        logger.info(f"📊 Total chunks: {stats['total_chunks']}")
        logger.info(f"📁 By module: {stats['by_module']}")
        logger.info(f"📑 By category: {stats['by_category']}")
        logger.info("="*70)
        
        self.monitor.log_metrics({
            'event': 'index_built',
            'total_chunks': stats['total_chunks'],
            'build_time_seconds': elapsed
        })
        
        return True
    
    def load_index(self):
        """Loads a previously built index"""
        logger.info("📂 Loading existing index...")

        try:
            self.vector_store.load(self.config.embeddings_path)

            # Load BM25
            import pickle
            bm25_path = os.path.join(self.config.embeddings_path, "bm25.pkl")

            if os.path.exists(bm25_path):
                with open(bm25_path, 'rb') as f:
                    bm25_data = pickle.load(f)

                self.hybrid_search = HybridSearch(
                    self.vector_store,
                    self.embedding_generator
                )
                self.hybrid_search.bm25 = bm25_data['bm25']
                self.hybrid_search.tokenized_corpus = bm25_data['tokenized_corpus']

                logger.info("✅ BM25 index loaded")
            else:
                logger.warning("⚠️  BM25 index not found, rebuilding...")
                self.hybrid_search = HybridSearch(
                    self.vector_store,
                    self.embedding_generator
                )
                self.hybrid_search.build_bm25_index()

            logger.info("✅ Index loaded successfully")

            stats = self.vector_store.get_statistics()
            logger.info(f"📊 Available chunks: {stats['total_chunks']}")

            return True

        except Exception as e:
            logger.error(f"❌ Error loading index: {str(e)}")
            return False
    
    def query(
        self,
        question: str,
        k: int | None= None,
        filters: Dict | None = None,
        use_cache: bool = True,
        stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Performs a query to the RAG"""

        start_time = time.time()

        # Check cache
        if use_cache and self.cache:
            cached_response = self.cache.get_response(question)
            if cached_response:
                elapsed = time.time() - start_time
                self.monitor.log_query(
                    query=question,
                    num_chunks=0,
                    response_time=elapsed,
                    cache_hit=True
                )
                return cached_response

        try:
            # 1. Retrieve relevant chunks
            logger.info(f"🔍 Searching information for: {question[:100]}...")

            k = k or self.config.search.top_k

            if self.hybrid_search:
                relevant_chunks = self.hybrid_search.search(
                    query=question,
                    k=k,
                    alpha=self.config.search.hybrid_alpha,
                    filters=filters
                )
            else:
                query_embedding = self.embedding_generator.generate_query_embedding(question)
                relevant_chunks = self.vector_store.search(
                    query_embedding,
                    k=k,
                    filters=filters
                )

            logger.info(f"✅ Found {len(relevant_chunks)} relevant chunks")

            for i, chunk_data in enumerate(relevant_chunks[:3], 1):
                metadata = chunk_data.get('metadata', {})
                score = chunk_data.get('combined_score', chunk_data.get('similarity', 0))
                logger.debug(f"  {i}. {metadata.get('filename')} (score: {score:.3f})")

            # 2. Build prompt
            logger.info("📝 Building prompt...")
            prompt = self.prompt_builder.build_prompt(question, relevant_chunks)

            # 3. Generate response
            logger.info("🤖 Generating response with Claude...")

            if stream:
                response_generator = self.claude_client.generate_response_streaming(
                    prompt,
                    max_tokens=self.config.claude.max_tokens,
                    temperature=self.config.claude.temperature
                )

                elapsed = time.time() - start_time
                self.monitor.log_query(
                    query=question,
                    num_chunks=len(relevant_chunks),
                    response_time=elapsed,
                    cache_hit=False
                )

                return response_generator
            else:
                response = self.claude_client.generate_response(
                    prompt,
                    max_tokens=self.config.claude.max_tokens,
                    temperature=self.config.claude.temperature
                )

            elapsed = time.time() - start_time

            logger.info(f"✅ Response generated in {elapsed:.2f}s")

            # Cache response
            if use_cache and self.cache:
                self.cache.set_response(question, response)

            # Log query
            self.monitor.log_query(
                query=question,
                num_chunks=len(relevant_chunks),
                response_time=elapsed,
                cache_hit=False
            )

            return response

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ Error processing query: {str(e)}")

            self.monitor.log_query(
                query=question,
                num_chunks=0,
                response_time=elapsed,
                cache_hit=False,
                error=str(e)
            )

            raise
    
    def get_relevant_chunks(
        self,
        question: str,
        k: int | None= None,
        filters: Dict | None = None
    ) -> List[Dict]:
        """Only retrieves relevant chunks without generating a response"""
        k = k or self.config.search.top_k

        if self.hybrid_search:
            return self.hybrid_search.search(
                query=question,
                k=k,
                alpha=self.config.search.hybrid_alpha,
                filters=filters
            )
        else:
            query_embedding = self.embedding_generator.generate_query_embedding(question)
            return self.vector_store.search(
                query_embedding,
                k=k,
                filters=filters
            )

    def get_statistics(self) -> Dict:
        """Gets system statistics"""
        stats = {
            'vector_store': self.vector_store.get_statistics(),
            'query_stats': self.monitor.get_query_stats(),
        }

        if self.cache:
            stats['cache'] = self.cache.get_stats()

        return stats
