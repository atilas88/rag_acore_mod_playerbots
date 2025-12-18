# Project Structure - AzerothCore RAG

## Directory Tree

```
azerothcore-rag/
├── configs/                      # Configuration files
│   └── config.yaml              # Main RAG configuration
│
├── data/                        # System data
│   ├── raw/                    # Original documentation (clone repos here)
│   ├── processed/              # Processed documents
│   ├── embeddings/             # Vector indexes (FAISS + BM25)
│   └── cache/                  # Response cache
│
├── logs/                        # Log files
│   └── rag.log                 # Main log (auto-generated)
│
├── scripts/                     # Utility scripts
│   ├── __init__.py
│   ├── build_index.py          # Build index from scratch
│   ├── update_index.py         # Update index incrementally
│   └── evaluate.py             # Evaluate system quality
│
├── src/                         # Main source code
│   ├── __init__.py
│   │
│   ├── preprocessing/          # Preprocessing module
│   │   ├── __init__.py
│   │   ├── document_loader.py  # Loads documents
│   │   ├── document_cleaner.py # Cleans and normalizes
│   │   ├── chunker.py          # Splits into intelligent chunks
│   │   └── metadata_extractor.py # Extracts metadata
│   │
│   ├── indexing/               # Indexing module
│   │   ├── __init__.py
│   │   ├── embedding_generator.py # Generates embeddings
│   │   ├── vector_store.py     # Stores vectors (FAISS)
│   │   └── hybrid_search.py    # Hybrid search (semantic + BM25)
│   │
│   ├── retrieval/              # Retrieval module (future)
│   │   └── __init__.py
│   │
│   ├── generation/             # Generation module
│   │   ├── __init__.py
│   │   ├── claude_client.py    # Claude client
│   │   └── prompt_builder.py   # Builds specialized prompts
│   │
│   ├── config.py               # Configuration system
│   ├── pipeline.py             # Main RAG pipeline
│   ├── cache.py                # Cache system
│   └── monitor.py              # Monitoring and metrics
│
├── tests/                       # Tests and validation
│   ├── __init__.py
│   ├── test_structure.py       # Verifies project structure
│   └── test_queries.json       # Test queries for evaluation
│
├── .gitignore                   # Files ignored by git
├── main.py                      # Main application (interactive interface)
├── README.md                    # Main documentation
├── requirements.txt             # Python dependencies
└── setup.sh                     # Installation script
```

## Module Descriptions

### 📦 Preprocessing (`src/preprocessing/`)
Responsible for loading and preparing documents for indexing:
- **DocumentLoader**: Traverses directories and loads files (.cpp, .h, .md, .conf, .sql)
- **DocumentCleaner**: Cleans code (comments, whitespace, etc.)
- **SmartChunker**: Intelligently splits documents based on type
- **MetadataExtractor**: Extracts useful information (module, category, tags)

### 🔍 Indexing (`src/indexing/`)
Handles embeddings and search:
- **EmbeddingGenerator**: Generates vectors using sentence-transformers
- **VectorStore**: Stores and searches using FAISS
- **HybridSearch**: Combines semantic search + keywords (BM25)

### 🤖 Generation (`src/generation/`)
Generates responses with Claude:
- **ClaudeClient**: Interacts with Anthropic API
- **PromptBuilder**: Builds specialized prompts based on query type

### ⚙️ Utilities (`src/`)
- **config.py**: Flexible configuration system
- **pipeline.py**: Orchestrates the entire RAG flow
- **cache.py**: Response cache for better performance
- **monitor.py**: System logging and metrics

## Data Flow

### 1. Index Building (build_index.py)
```
Raw documents → DocumentLoader → DocumentCleaner → SmartChunker
    → MetadataExtractor → EmbeddingGenerator → VectorStore
```

### 2. User Query (main.py)
```
Query → HybridSearch (semantic + BM25) → Relevant chunks
    → PromptBuilder → ClaudeClient → Response
```

### 3. Update (update_index.py)
```
Git log → Modified files → Processing → Index update
```

## Current Status

### ✅ Completed
- [x] Directory structure
- [x] Configuration files (config.yaml)
- [x] Requirements and setup
- [x] README and documentation
- [x] Structure tests
- [x] Placeholder files for all modules

### ⏳ Pending (next phase)
- [ ] Implement src/config.py
- [ ] Implement preprocessing modules
- [ ] Implement indexing modules
- [ ] Implement generation modules
- [ ] Implement utilities (cache, monitor)
- [ ] Implement pipeline
- [ ] Implement scripts
- [ ] Implement main.py

## Next Steps

1. **Configure virtual environment**
   ```bash
   ./setup.sh
   ```

2. **Implement modules in order**
   - Phase 1: config.py
   - Phase 2: preprocessing/
   - Phase 3: indexing/
   - Phase 4: generation/
   - Phase 5: pipeline.py
   - Phase 6: scripts and main.py

3. **Download documentation**
   ```bash
   cd data/raw
   git clone https://github.com/azerothcore/azerothcore-wotlk.git
   ```

4. **Build and test**
   ```bash
   python scripts/build_index.py
   python main.py
   ```
