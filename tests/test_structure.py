#!/usr/bin/env python3
# tests/test_structure.py
"""
Tests para verificar que la estructura del proyecto está correcta
"""

import os
import sys
from pathlib import Path

def test_project_structure():
    """Verifica que todos los directorios existen"""
    base_dir = Path(__file__).parent.parent

    required_dirs = [
        'src',
        'src/preprocessing',
        'src/indexing',
        'src/retrieval',
        'src/generation',
        'data',
        'data/raw',
        'data/processed',
        'data/embeddings',
        'data/cache',
        'configs',
        'scripts',
        'tests',
        'logs'
    ]

    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        assert full_path.exists(), f"Directorio faltante: {dir_path}"
        assert full_path.is_dir(), f"No es un directorio: {dir_path}"

    print("✅ Todos los directorios existen")

def test_required_files():
    """Verifica que los archivos esenciales existen"""
    base_dir = Path(__file__).parent.parent

    required_files = [
        'requirements.txt',
        'README.md',
        '.gitignore',
        'setup.sh',
        'main.py',
        'configs/config.yaml',
        'tests/test_queries.json',
        'src/__init__.py',
        'src/config.py',
        'src/pipeline.py',
        'src/cache.py',
        'src/monitor.py',
    ]

    for file_path in required_files:
        full_path = base_dir / file_path
        assert full_path.exists(), f"Archivo faltante: {file_path}"
        assert full_path.is_file(), f"No es un archivo: {file_path}"

    print("✅ Todos los archivos esenciales existen")

def test_python_modules():
    """Verifica que los módulos Python tienen __init__.py"""
    base_dir = Path(__file__).parent.parent

    python_modules = [
        'src',
        'src/preprocessing',
        'src/indexing',
        'src/retrieval',
        'src/generation',
        'scripts',
        'tests'
    ]

    for module_path in python_modules:
        init_file = base_dir / module_path / '__init__.py'
        assert init_file.exists(), f"Falta __init__.py en: {module_path}"

    print("✅ Todos los módulos tienen __init__.py")

if __name__ == "__main__":
    print("\n🧪 VERIFICANDO ESTRUCTURA DEL PROYECTO")
    print("="*70)

    try:
        test_project_structure()
        test_required_files()
        test_python_modules()

        print("="*70)
        print("✅ ESTRUCTURA DEL PROYECTO CORRECTA\n")

    except AssertionError as e:
        print(f"\n❌ ERROR: {e}\n")
        sys.exit(1)
