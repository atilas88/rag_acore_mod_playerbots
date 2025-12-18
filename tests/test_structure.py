#!/usr/bin/env python3
# tests/test_structure.py
"""
Tests to verify that the project structure is correct
"""

import os
import sys
from pathlib import Path

def test_project_structure():
    """Verifies that all directories exist"""
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
        assert full_path.exists(), f"Missing directory: {dir_path}"
        assert full_path.is_dir(), f"Not a directory: {dir_path}"

    print("✅ All directories exist")

def test_required_files():
    """Verifies that essential files exist"""
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
        assert full_path.exists(), f"Missing file: {file_path}"
        assert full_path.is_file(), f"Not a file: {file_path}"

    print("✅ All essential files exist")

def test_python_modules():
    """Verifies that Python modules have __init__.py"""
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
        assert init_file.exists(), f"Missing __init__.py in: {module_path}"

    print("✅ All modules have __init__.py")

if __name__ == "__main__":
    print("\n🧪 VERIFYING PROJECT STRUCTURE")
    print("="*70)

    try:
        test_project_structure()
        test_required_files()
        test_python_modules()

        print("="*70)
        print("✅ PROJECT STRUCTURE CORRECT\n")

    except AssertionError as e:
        print(f"\n❌ ERROR: {e}\n")
        sys.exit(1)
