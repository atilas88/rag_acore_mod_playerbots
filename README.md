# RAG AzerothCore

Retrieval-Augmented Generation (RAG) system specialized in AzerothCore and mod-playerbots documentation, using Claude as the language model.

## Features

- **Hybrid search**: Combines semantic search (embeddings) with keyword search (BM25)
- **Intelligent chunking**: Splits documents based on their type (C++, Markdown, configs)
- **Enriched metadata**: Extracts useful information from each document
- **Response caching**: Speeds up repeated queries
- **Specialized prompts**: Different prompts based on question type
- **Monitoring and metrics**: Performance and usage tracking

## Project Structure

```
azerothcore-rag/
├── src/
│   ├── preprocessing/      # Document loading and processing
│   ├── indexing/          # Embeddings and vector search
│   ├── retrieval/         # Information retrieval
│   ├── generation/        # Claude generation
│   ├── config.py          # Configuration
│   ├── pipeline.py        # Main pipeline
│   ├── cache.py           # Cache system
│   └── monitor.py         # Monitoring
├── data/
│   ├── raw/              # Original documentation
│   ├── processed/        # Processed documents
│   ├── embeddings/       # Vector indexes
│   └── cache/            # Response cache
├── configs/
│   └── config.yaml       # Main configuration
├── scripts/
│   ├── build_index.py    # Build index
│   ├── update_index.py   # Update index
│   └── evaluate.py       # Evaluate system
├── tests/
│   └── test_queries.json # Test queries
├── main.py               # Main application
└── requirements.txt      # Dependencies
```

## Installation

### 1. Clone the repository

```bash
git clone <your-repo>
cd azerothcore-rag
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Anthropic API Key

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

### 5. Download AzerothCore documentation

```bash
cd data/raw
git clone https://github.com/azerothcore/azerothcore-wotlk.git
cd ../..
```

## Usage

### Build the index

First time (builds index from scratch):

```bash
python scripts/build_index.py
```

This process:
1. Loads documents from `data/raw/`
2. Cleans and splits them into chunks
3. Generates embeddings
4. Builds vector and BM25 indexes
5. Saves everything to `data/embeddings/`

### Run the system

```bash
python main.py
```

Available commands:
- `/help` - Show help
- `/stats` - System statistics
- `/cache` - Cache information
- `/clear` - Clear cache
- `/filters` - Configure search filters
- `/exit` - Exit

### Usage example

```
💬 Your question: How do I configure bots to use potions?

🔍 Searching information...

======================================================================
💡 ANSWER:
======================================================================

To configure bots to automatically use potions in AzerothCore
with mod-playerbots, you need to modify the configuration file...

[rest of the answer]
======================================================================
```

### Update the index

To update with new documentation:

```bash
python scripts/update_index.py
```

### Evaluate the system

```bash
python scripts/evaluate.py
```

## Configuration

Edit `configs/config.yaml` to adjust:

- **Chunking**: Chunk size, overlap
- **Embeddings**: Model, dimension, batch size
- **Search**: Top K, hybrid balance (alpha)
- **Claude**: Model, temperature, max tokens
- **Cache**: Enabled, TTL

## Data Structure

### Chunks

Documents are split into chunks with metadata:

```python
{
    'content': 'chunk text',
    'chunk_index': 0,
    'metadata': {
        'filename': 'PlayerbotAI.cpp',
        'filepath': 'src/PlayerbotAI.cpp',
        'type': 'cpp',
        'module': 'playerbots',
        'category': 'ai',
        'tags': ['PlayerbotAI', 'UpdateAI'],
        'has_config': False,
        'has_example': True
    }
}
```

### Hybrid Search

The system combines:
- **Semantic search** (embeddings): Captures meaning
- **Keyword search** (BM25): Finds exact terms

Balance controlled by `hybrid_alpha` (0.0 = keywords only, 1.0 = semantic only)

## Troubleshooting

### Error: Index not found

```bash
python scripts/build_index.py
```

### Error: API Key not configured

```bash
export ANTHROPIC_API_KEY='your-key'
```

### Low quality responses

1. Increase `top_k` in config.yaml
2. Adjust `hybrid_alpha`
3. Use specific filters (`/filters`)

### Slow performance

1. Enable cache (`cache.enabled: true`)
2. Reduce `chunk_size`
3. Adjust `batch_size`

## Development

### Run tests

```bash
pytest tests/
```

### View logs

```bash
tail -f logs/rag.log
```
