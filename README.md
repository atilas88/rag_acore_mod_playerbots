# RAG AzerothCore

Sistema de Retrieval-Augmented Generation (RAG) especializado en documentación de AzerothCore y mod-playerbots, usando Claude como modelo de lenguaje.

## Características

- **Búsqueda híbrida**: Combina búsqueda semántica (embeddings) con búsqueda por keywords (BM25)
- **Chunking inteligente**: Divide documentos según su tipo (C++, Markdown, configs)
- **Metadata enriquecida**: Extrae información útil de cada documento
- **Caché de respuestas**: Acelera queries repetidas
- **Prompts especializados**: Diferentes prompts según el tipo de pregunta
- **Monitoreo y métricas**: Tracking de performance y uso

## Estructura del Proyecto

```
azerothcore-rag/
├── src/
│   ├── preprocessing/      # Carga y procesamiento de documentos
│   ├── indexing/          # Embeddings y búsqueda vectorial
│   ├── retrieval/         # Recuperación de información
│   ├── generation/        # Generación con Claude
│   ├── config.py          # Configuración
│   ├── pipeline.py        # Pipeline principal
│   ├── cache.py           # Sistema de caché
│   └── monitor.py         # Monitoreo
├── data/
│   ├── raw/              # Documentación original
│   ├── processed/        # Documentos procesados
│   ├── embeddings/       # Índices vectoriales
│   └── cache/            # Caché de respuestas
├── configs/
│   └── config.yaml       # Configuración principal
├── scripts/
│   ├── build_index.py    # Construir índice
│   ├── update_index.py   # Actualizar índice
│   └── evaluate.py       # Evaluar sistema
├── tests/
│   └── test_queries.json # Queries de prueba
├── main.py               # Aplicación principal
└── requirements.txt      # Dependencias
```

## Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repo>
cd azerothcore-rag
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar API Key de Anthropic

```bash
export ANTHROPIC_API_KEY='tu-api-key-aqui'
```

### 5. Descargar documentación de AzerothCore

```bash
cd data/raw
git clone https://github.com/azerothcore/azerothcore-wotlk.git
cd ../..
```

## Uso

### Construir el índice

Primera vez (construye índice desde cero):

```bash
python scripts/build_index.py
```

Este proceso:
1. Carga documentos desde `data/raw/`
2. Los limpia y divide en chunks
3. Genera embeddings
4. Construye índice vectorial y BM25
5. Guarda todo en `data/embeddings/`

### Ejecutar el sistema

```bash
python main.py
```

Comandos disponibles:
- `/help` - Muestra ayuda
- `/stats` - Estadísticas del sistema
- `/cache` - Información del caché
- `/clear` - Limpiar caché
- `/filters` - Configurar filtros de búsqueda
- `/exit` - Salir

### Ejemplo de uso

```
💬 Tu pregunta: ¿Cómo configuro que los bots usen pociones?

🔍 Buscando información...

======================================================================
💡 RESPUESTA:
======================================================================

Para configurar que los bots usen pociones automáticamente en AzerothCore
con mod-playerbots, necesitas modificar el archivo de configuración...

[resto de la respuesta]
======================================================================
```

### Actualizar el índice

Para actualizar con documentación nueva:

```bash
python scripts/update_index.py
```

### Evaluar el sistema

```bash
python scripts/evaluate.py
```

## Configuración

Edita `configs/config.yaml` para ajustar:

- **Chunking**: Tamaño de chunks, overlap
- **Embeddings**: Modelo, dimensión, batch size
- **Búsqueda**: Top K, balance híbrido (alpha)
- **Claude**: Modelo, temperatura, max tokens
- **Caché**: Habilitado, TTL

## Estructura de Datos

### Chunks

Los documentos se dividen en chunks con metadata:

```python
{
    'content': 'texto del chunk',
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

### Búsqueda Híbrida

El sistema combina:
- **Búsqueda semántica** (embeddings): Captura significado
- **Búsqueda por keywords** (BM25): Encuentra términos exactos

Balance controlado por `hybrid_alpha` (0.0 = solo keywords, 1.0 = solo semántica)

## Troubleshooting

### Error: No se encuentra el índice

```bash
python scripts/build_index.py
```

### Error: API Key no configurada

```bash
export ANTHROPIC_API_KEY='tu-key'
```

### Respuestas de baja calidad

1. Aumenta `top_k` en config.yaml
2. Ajusta `hybrid_alpha`
3. Usa filtros específicos (`/filters`)

### Performance lento

1. Habilita caché (`cache.enabled: true`)
2. Reduce `chunk_size`
3. Ajusta `batch_size`

## Desarrollo

### Ejecutar tests

```bash
pytest tests/
```

### Ver logs

```bash
tail -f logs/rag.log
```

