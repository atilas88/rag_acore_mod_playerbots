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
    """Pipeline completo del RAG"""
    
    def __init__(self, config: Config, api_key: str):
        self.config = config
        
        # Componentes
        self.document_loader = DocumentLoader(config)
        self.embedding_generator = EmbeddingGenerator(config.embedding.model_name)
        self.vector_store = VectorStore(dimension=config.embedding.dimension)
        self.hybrid_search = None
        self.claude_client = ClaudeClient(api_key=api_key, model=config.claude.model)
        self.prompt_builder = PromptBuilder()
        
        # Utilidades
        if config.cache.enabled:
            self.cache = RAGCache(
                cache_dir=config.cache.cache_dir,
                ttl_days=config.cache.ttl_days
            )
        else:
            self.cache = None
        
        self.monitor = RAGMonitor()
        
        logger.info("✅ RAGPipeline inicializado")
    
    def build_index(self, force_rebuild: bool = False):
        """Construye el índice completo desde cero"""
        
        logger.info("🏗️  CONSTRUYENDO ÍNDICE DEL RAG")
        logger.info("="*70)
        
        start_time = time.time()
        
        # 1. Cargar documentos
        logger.info("PASO 1: Cargando documentos...")
        documents = self.document_loader.load_documents(self.config.raw_data_path)
        
        if not documents:
            logger.error("❌ No se encontraron documentos")
            return False
        
        # 2. Procesar en chunks
        logger.info("PASO 2: Procesando documentos en chunks...")
        chunks = self.document_loader.process_documents(documents)
        
        if not chunks:
            logger.error("❌ No se generaron chunks")
            return False
        
        # 3. Generar embeddings
        logger.info("PASO 3: Generando embeddings...")
        chunks_with_embeddings = self.embedding_generator.generate_embeddings(
            chunks,
            batch_size=self.config.embedding.batch_size
        )
        
        # 4. Añadir al vector store
        logger.info("PASO 4: Construyendo vector store...")
        self.vector_store.add_chunks(chunks_with_embeddings)
        
        # 5. Construir índice BM25
        logger.info("PASO 5: Construyendo índice BM25...")
        self.hybrid_search = HybridSearch(self.vector_store, self.embedding_generator)
        self.hybrid_search.build_bm25_index()
        
        # 6. Guardar índice
        logger.info("PASO 6: Guardando índice...")
        self.vector_store.save(self.config.embeddings_path)
        
        # Guardar BM25
        import pickle
        bm25_path = os.path.join(self.config.embeddings_path, "bm25.pkl")
        with open(bm25_path, 'wb') as f:
            pickle.dump({
                'bm25': self.hybrid_search.bm25,
                'tokenized_corpus': self.hybrid_search.tokenized_corpus
            }, f)
        
        elapsed = time.time() - start_time
        
        # Estadísticas
        stats = self.vector_store.get_statistics()
        
        logger.info("="*70)
        logger.info("✅ ÍNDICE CONSTRUIDO EXITOSAMENTE")
        logger.info(f"⏱️  Tiempo total: {elapsed:.2f} segundos")
        logger.info(f"📊 Total chunks: {stats['total_chunks']}")
        logger.info(f"📁 Por módulo: {stats['by_module']}")
        logger.info(f"📑 Por categoría: {stats['by_category']}")
        logger.info("="*70)
        
        self.monitor.log_metrics({
            'event': 'index_built',
            'total_chunks': stats['total_chunks'],
            'build_time_seconds': elapsed
        })
        
        return True
    
    def load_index(self):
        """Carga un índice previamente construido"""
        logger.info("📂 Cargando índice existente...")
        
        try:
            self.vector_store.load(self.config.embeddings_path)
            
            # Cargar BM25
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
                
                logger.info("✅ Índice BM25 cargado")
            else:
                logger.warning("⚠️  No se encontró índice BM25, reconstruyendo...")
                self.hybrid_search = HybridSearch(
                    self.vector_store,
                    self.embedding_generator
                )
                self.hybrid_search.build_bm25_index()
            
            logger.info("✅ Índice cargado exitosamente")
            
            stats = self.vector_store.get_statistics()
            logger.info(f"📊 Chunks disponibles: {stats['total_chunks']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando índice: {str(e)}")
            return False
    
    def query(
        self,
        question: str,
        k: int | None= None,
        filters: Dict | None = None,
        use_cache: bool = True,
        stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Realiza una consulta al RAG"""
        
        start_time = time.time()
        
        # Verificar caché
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
            # 1. Recuperar chunks relevantes
            logger.info(f"🔍 Buscando información para: {question[:100]}...")
            
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
            
            logger.info(f"✅ Encontrados {len(relevant_chunks)} chunks relevantes")
            
            for i, chunk_data in enumerate(relevant_chunks[:3], 1):
                metadata = chunk_data.get('metadata', {})
                score = chunk_data.get('combined_score', chunk_data.get('similarity', 0))
                logger.debug(f"  {i}. {metadata.get('filename')} (score: {score:.3f})")
            
            # 2. Construir prompt
            logger.info("📝 Construyendo prompt...")
            prompt = self.prompt_builder.build_prompt(question, relevant_chunks)
            
            # 3. Generar respuesta
            logger.info("🤖 Generando respuesta con Claude...")
            
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
            
            logger.info(f"✅ Respuesta generada en {elapsed:.2f}s")
            
            # Cachear respuesta
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
            logger.error(f"❌ Error procesando query: {str(e)}")
            
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
        """Solo recupera chunks relevantes sin generar respuesta"""
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
        """Obtiene estadísticas del sistema"""
        stats = {
            'vector_store': self.vector_store.get_statistics(),
            'query_stats': self.monitor.get_query_stats(),
        }
        
        if self.cache:
            stats['cache'] = self.cache.get_stats()
        
        return stats
