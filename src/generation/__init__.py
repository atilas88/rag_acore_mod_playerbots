# src/generation/__init__.py
"""
Módulo de generación de respuestas con Claude
"""

from .claude_client import ClaudeClient
from .prompt_builder import PromptBuilder

__all__ = [
    'ClaudeClient',
    'PromptBuilder'
]
