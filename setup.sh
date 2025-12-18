#!/bin/bash
# setup.sh - Quick setup script

echo "🚀 SETUP RAG AZEROTHCORE"
echo "========================"
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# 2. Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# 3. Activate environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# 4. Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create directories (should already exist, but just in case)
echo "📁 Verifying directory structure..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/embeddings
mkdir -p data/cache
mkdir -p logs

# 6. Check API Key
echo ""
echo "🔑 API Key Configuration:"
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not configured"
    echo "   Configure it with: export ANTHROPIC_API_KEY='your-api-key'"
else
    echo "✅ ANTHROPIC_API_KEY configured"
fi

# 7. Final instructions
echo ""
echo "======================================================================"
echo "✅ SETUP COMPLETED"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. Configure your Anthropic API Key:"
echo "   export ANTHROPIC_API_KEY='your-api-key'"
echo ""
echo "2. Download AzerothCore documentation to ./data/raw/"
echo "   cd data/raw"
echo "   git clone https://github.com/azerothcore/azerothcore-wotlk.git"
echo "   cd ../.."
echo ""
echo "3. Build the index:"
echo "   python scripts/build_index.py"
echo ""
echo "4. Run the system:"
echo "   python main.py"
echo ""
echo "For more information, see README.md"
echo ""
