# src/preprocessing/document_loader.py
"""
Loads and processes documents from the file system
"""
import os
from pathlib import Path
from typing import List, Dict
from .document_cleaner import DocumentCleaner
from .metadata_extractor import MetadataExtractor
from .chunker import SmartChunker
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Load and process documents from the file system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.cleaner = DocumentCleaner()
        self.metadata_extractor = MetadataExtractor()
        # config.chunking is guaranteed to be non-None after __post_init__
        assert config.chunking is not None
        self.chunker = SmartChunker(config.chunking)
        
        self.supported_extensions = {'.cpp', '.h', '.md', '.conf', '.sql', '.txt'}
    
    def load_documents(self, directory: str) -> List[Dict]:
        """Load all documents from a directory"""
        logger.info(f"📂 Loading documents from: {directory}")
        
        documents = []
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in {
                '.git', '__pycache__', 'build', '.vscode'
            }]
            
            for file in files:
                file_path = os.path.join(root, file)
                ext = Path(file).suffix
                
                if ext not in self.supported_extensions:
                    continue
                
                try:
                    doc = self._load_single_document(file_path)
                    if doc:
                        documents.append(doc)
                except Exception as e:
                    logger.error(f"❌ Error loading {file_path}: {str(e)}")
        
        logger.info(f"✅ Loaded {len(documents)} documents")
        return documents
    
    def _load_single_document(self, filepath: str) -> Dict | None:
        """Load a single document"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"⚠️  Could not read {filepath}: {str(e)}")
            return None
        
        if not content.strip():
            return None
        
        file_ext = Path(filepath).suffix[1:]
        cleaned_content = self.cleaner.clean(content, file_ext)
        
        metadata = self.metadata_extractor.extract(cleaned_content, filepath)
        
        return {
            'content': cleaned_content,
            'metadata': metadata
        }
    
    def process_documents(self, documents: List[Dict]) -> List[Dict]:
        """Process documents into chunks"""
        logger.info(f"✂️  Processing {len(documents)} documents...")
        
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunker.chunk_document(
                doc['content'],
                doc['metadata']
            )
            all_chunks.extend(chunks)
        
        logger.info(f"✅ Created {len(all_chunks)} chunks")
        return all_chunks
