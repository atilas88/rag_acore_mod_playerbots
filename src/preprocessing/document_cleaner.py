# src/preprocessing/document_cleaner.py
"""
Cleans and normalizes documents
"""
import re
from typing import List

class DocumentCleaner:
    
    def clean(self, content: str, file_type: str) -> str:
        if file_type in ['cpp','h']:
            return self._clean_cpp(content)
        elif file_type == 'md':
            return self._clean_markdown(content)
        elif file_type == 'conf':
            return self._clean_config(content)
        else:
            return self._clean_generic(content)
        
    def _clean_cpp(self, content: str) -> str:
        """Clean c++ source files"""
        # Remove copyright comments
        content = re.sub(
            r'/\*[\s\S]*?Copyright[\s\S]*?\*/',
            '',
            content
        )
                
        # Remove excessive whitespace
        content = self._remove_whitespaces_helper(content)
        
        # Normalize line indentation
        lines = content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        content = '\n'.join(cleaned_lines)
        
        return content.strip()
    
    def _clean_markdown(self, content: str) -> str:
        """Clean markdown files"""
        # Remove images (kept alt text)
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', content)
        
        # Normalize headers
        content = re.sub(r'#{1,6}\s+', lambda m: m.group(0).strip() + ' ', content)
        
        # Remove excessive whitespace
        content = self._remove_whitespaces_helper(content)
        
        return content.strip()
    
    def _clean_config(self, content: str) -> str:
        """Clean configuration files"""
        lines = []
        for line in content.split('\n'):
            if line.strip() and not line.strip().startswith('##'):
                lines.append(line.rstrip())
        
        return '\n'.join(lines)
    
    def _clean_generic(self, content: str) -> str:
        """Clean generic text files"""
        content = self._remove_whitespaces_helper(content)
        return content.strip()
    
    def _remove_whitespaces_helper(self, content: str) -> str:
        """Remove excessive whitespaces"""
        return re.sub(r'\n\s*\n\s*\n+', '\n\n', content)