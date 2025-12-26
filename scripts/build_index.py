#!/usr/bin/env python3
# scripts/build_index.py
"""
Script to build the RAG index from scratch
"""
import os
import sys
from pathlib import Path
import subprocess
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.pipeline import RAGPipeline
from src.preprocessing.document_loader import DocumentLoader
import logging

logger = logging.getLogger(__name__)

class IncrementalUpdater:
    """Updates the index incrementally"""

    def __init__(self, pipeline: RAGPipeline, repo_path: str):
        self.pipeline = pipeline
        self.repo_path = repo_path
        self.last_update_file = Path("./data/last_update.txt")

    def update(self):
        """Updates the index with modified files"""
        
        last_update = self._get_last_update()

        print(f"📅 Last update: {last_update}")
        print("🔍 Searching for modified files since then...")

        modified_files = self._get_modified_files(last_update)

        if not modified_files:
            print("✅ No modified files. Index is up to date.")
            return

        print(f"📝 Found {len(modified_files)} modified files")
        for f in modified_files[:10]:
            print(f"   - {f}")
        if len(modified_files) > 10:
            print(f"   ... and {len(modified_files) - 10} more")

        print("\n🔄 Processing modified files...")
        
        doc_loader = self.pipeline.document_loader
        new_documents = []
        
        for filepath in modified_files:
            full_path = os.path.join(self.repo_path, filepath)
            if os.path.exists(full_path):
                doc = doc_loader._load_single_document(full_path)
                if doc:
                    new_documents.append(doc)
        
        if not new_documents:
            print("⚠️  Could not process modified files")
            return

        new_chunks = doc_loader.process_documents(new_documents)

        print("🧮 Generating embeddings...")
        chunks_with_embeddings = self.pipeline.embedding_generator.generate_embeddings(
            new_chunks,
            batch_size=self.pipeline.config.embedding.batch_size
        )

        print("💾 Updating vector store...")
        self.pipeline.vector_store.add_chunks(chunks_with_embeddings)

        print("📊 Rebuilding BM25 index...")
        self.pipeline.hybrid_search.build_bm25_index()

        print("💾 Saving updated index...")
        self.pipeline.vector_store.save(self.pipeline.config.embeddings_path)
        
        import pickle
        bm25_path = os.path.join(self.pipeline.config.embeddings_path, "bm25.pkl")
        with open(bm25_path, 'wb') as f:
            pickle.dump({
                'bm25': self.pipeline.hybrid_search.bm25,
                'tokenized_corpus': self.pipeline.hybrid_search.tokenized_corpus
            }, f)
        
        self._save_update_time()

        print(f"\n✅ Index updated with {len(new_chunks)} new chunks")

    def _get_last_update(self) -> str:
        """Gets the timestamp of the last update"""
        if self.last_update_file.exists():
            with open(self.last_update_file, 'r') as f:
                return f.read().strip()
        else:
            return "30 days ago"
    
    def _get_modified_files(self, since: str) -> list:
        """Gets files modified since 'since'"""
        try:
            cmd = [
                'git', 'log',
                f'--since={since}',
                '--name-only',
                '--pretty=format:',
                '--diff-filter=AM'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            files = set(result.stdout.strip().split('\n'))
            relevant_extensions = {'.cpp', '.h', '.md', '.conf', '.sql'}
            
            filtered_files = [
                f for f in files 
                if f and Path(f).suffix in relevant_extensions
            ]
            
            return filtered_files
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing git: {e}")
            return []

    def _save_update_time(self):
        """Saves update timestamp"""
        with open(self.last_update_file, 'w') as f:
            f.write(datetime.now().isoformat())

def main():
    config = Config.from_yaml("./configs/config.yaml") if os.path.exists("./configs/config.yaml") else Config()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not configured")
        sys.exit(1)

    repo_path = input("Path to AzerothCore repository (Enter for ./data/raw): ").strip()
    if not repo_path:
        repo_path = "./data/raw"

    if not os.path.exists(repo_path):
        print(f"❌ ERROR: {repo_path} does not exist")
        sys.exit(1)

    print("\n🔄 INCREMENTAL INDEX UPDATE")
    print("="*70 + "\n")
    
    pipeline = RAGPipeline(config, api_key)
    
    if not pipeline.load_index():
        print("❌ Could not load existing index")
        print("   Run build_index.py first")
        sys.exit(1)
    
    updater = IncrementalUpdater(pipeline, repo_path)
    updater.update()

if __name__ == "__main__":
    main()
