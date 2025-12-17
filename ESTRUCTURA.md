# Estructura del Proyecto - AzerothCore RAG

## Árbol de Directorios

```
azerothcore-rag/
├── configs/                      # Archivos de configuración
│   └── config.yaml              # Configuración principal del RAG
│
├── data/                        # Datos del sistema
│   ├── raw/                    # Documentación original (clonar repos aquí)
│   ├── processed/              # Documentos procesados
│   ├── embeddings/             # Índices vectoriales (FAISS + BM25)
│   └── cache/                  # Caché de respuestas
│
├── logs/                        # Archivos de log
│   └── rag.log                 # Log principal (se genera automáticamente)
│
├── scripts/                     # Scripts de utilidad
│   ├── __init__.py
│   ├── build_index.py          # Construir índice desde cero
│   ├── update_index.py         # Actualizar índice incrementalmente
│   └── evaluate.py             # Evaluar calidad del sistema
│
├── src/                         # Código fuente principal
│   ├── __init__.py
│   │
│   ├── preprocessing/          # Módulo de preprocesamiento
│   │   ├── __init__.py
│   │   ├── document_loader.py  # Carga documentos
│   │   ├── document_cleaner.py # Limpia y normaliza
│   │   ├── chunker.py          # Divide en chunks inteligentes
│   │   └── metadata_extractor.py # Extrae metadata
│   │
│   ├── indexing/               # Módulo de indexing
│   │   ├── __init__.py
│   │   ├── embedding_generator.py # Genera embeddings
│   │   ├── vector_store.py     # Almacena vectores (FAISS)
│   │   └── hybrid_search.py    # Búsqueda híbrida (semántica + BM25)
│   │
│   ├── retrieval/              # Módulo de retrieval (futuro)
│   │   └── __init__.py
│   │
│   ├── generation/             # Módulo de generación
│   │   ├── __init__.py
│   │   ├── claude_client.py    # Cliente de Claude
│   │   └── prompt_builder.py   # Construye prompts especializados
│   │
│   ├── config.py               # Sistema de configuración
│   ├── pipeline.py             # Pipeline principal del RAG
│   ├── cache.py                # Sistema de caché
│   └── monitor.py              # Monitoreo y métricas
│
├── tests/                       # Tests y validación
│   ├── __init__.py
│   ├── test_structure.py       # Verifica estructura del proyecto
│   └── test_queries.json       # Queries de prueba para evaluación
│
├── .gitignore                   # Archivos ignorados por git
├── main.py                      # Aplicación principal (interfaz interactiva)
├── README.md                    # Documentación principal
├── requirements.txt             # Dependencias Python
└── setup.sh                     # Script de instalación
```

## Descripción de Módulos

### 📦 Preprocessing (`src/preprocessing/`)
Responsable de cargar y preparar documentos para indexing:
- **DocumentLoader**: Recorre directorios y carga archivos (.cpp, .h, .md, .conf, .sql)
- **DocumentCleaner**: Limpia código (comentarios, whitespace, etc.)
- **SmartChunker**: Divide documentos inteligentemente según tipo
- **MetadataExtractor**: Extrae información útil (módulo, categoría, tags)

### 🔍 Indexing (`src/indexing/`)
Maneja embeddings y búsqueda:
- **EmbeddingGenerator**: Genera vectores usando sentence-transformers
- **VectorStore**: Almacena y busca usando FAISS
- **HybridSearch**: Combina búsqueda semántica + keywords (BM25)

### 🤖 Generation (`src/generation/`)
Genera respuestas con Claude:
- **ClaudeClient**: Interactúa con API de Anthropic
- **PromptBuilder**: Construye prompts especializados según tipo de query

### ⚙️ Utilidades (`src/`)
- **config.py**: Sistema de configuración flexible
- **pipeline.py**: Orquesta todo el flujo del RAG
- **cache.py**: Caché de respuestas para mejor performance
- **monitor.py**: Logging y métricas del sistema

## Flujo de Datos

### 1. Construcción del Índice (build_index.py)
```
Documentos raw → DocumentLoader → DocumentCleaner → SmartChunker
    → MetadataExtractor → EmbeddingGenerator → VectorStore
```

### 2. Query del Usuario (main.py)
```
Query → HybridSearch (semántica + BM25) → Chunks relevantes
    → PromptBuilder → ClaudeClient → Respuesta
```

### 3. Actualización (update_index.py)
```
Git log → Archivos modificados → Procesamiento → Actualización índice
```

## Estado Actual

### ✅ Completado
- [x] Estructura de directorios
- [x] Archivos de configuración (config.yaml)
- [x] Requirements y setup
- [x] README y documentación
- [x] Tests de estructura
- [x] Archivos placeholder para todos los módulos

### ⏳ Pendiente (siguiente fase)
- [ ] Implementar src/config.py
- [ ] Implementar módulos de preprocessing
- [ ] Implementar módulos de indexing
- [ ] Implementar módulos de generation
- [ ] Implementar utilidades (cache, monitor)
- [ ] Implementar pipeline
- [ ] Implementar scripts
- [ ] Implementar main.py

## Próximos Pasos

1. **Configurar entorno virtual**
   ```bash
   ./setup.sh
   ```

2. **Implementar módulos en orden**
   - Fase 1: config.py
   - Fase 2: preprocessing/
   - Fase 3: indexing/
   - Fase 4: generation/
   - Fase 5: pipeline.py
   - Fase 6: scripts y main.py

3. **Descargar documentación**
   ```bash
   cd data/raw
   git clone https://github.com/azerothcore/azerothcore-wotlk.git
   ```

4. **Construir y probar**
   ```bash
   python scripts/build_index.py
   python main.py
   ```
