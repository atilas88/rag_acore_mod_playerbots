#!/bin/bash
# setup.sh - Script de configuración rápida

echo "🚀 SETUP RAG AZEROTHCORE"
echo "========================"
echo ""

# 1. Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# 2. Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# 3. Activar entorno
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# 4. Instalar dependencias
echo "📥 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Crear directorios (ya deberían existir, pero por si acaso)
echo "📁 Verificando estructura de directorios..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/embeddings
mkdir -p data/cache
mkdir -p logs

# 6. Verificar API Key
echo ""
echo "🔑 Configuración de API Key:"
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY no configurada"
    echo "   Configúrala con: export ANTHROPIC_API_KEY='tu-api-key'"
else
    echo "✅ ANTHROPIC_API_KEY configurada"
fi

# 7. Instrucciones finales
echo ""
echo "======================================================================"
echo "✅ SETUP COMPLETADO"
echo "======================================================================"
echo ""
echo "Próximos pasos:"
echo "1. Configura tu API Key de Anthropic:"
echo "   export ANTHROPIC_API_KEY='tu-api-key'"
echo ""
echo "2. Descarga la documentación de AzerothCore en ./data/raw/"
echo "   cd data/raw"
echo "   git clone https://github.com/azerothcore/azerothcore-wotlk.git"
echo "   cd ../.."
echo ""
echo "3. Construye el índice:"
echo "   python scripts/build_index.py"
echo ""
echo "4. Ejecuta el sistema:"
echo "   python main.py"
echo ""
echo "Para más información, consulta README.md"
echo ""
