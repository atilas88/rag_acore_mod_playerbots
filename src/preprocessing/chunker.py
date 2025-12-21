# src/preprocessing/chunker.py
"""
Splits documents into intelligent chunks based on their type
"""

import re
from typing import List, Dict
from src.config import ChunkingConfig

class SmartChunker:
    """Intelligent chunking based on content type"""
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
    
    def chunk_document(self, content: str, metadata: Dict) -> List[Dict]:
        """Chunks document according to its type"""
        file_type = metadata.get('type', 'txt')
        
        if file_type in ['cpp', 'h']:
            chunks = self._chunk_cpp(content)
        elif file_type == 'md':
            chunks = self._chunk_markdown(content)
        elif file_type == 'conf':
            chunks = self._chunk_config(content)
        else:
            chunks = self._chunk_generic(content)
        
        # Enrich chunks with metadata
        enriched_chunks = []
        for i, chunk_content in enumerate(chunks):
            if len(chunk_content.strip()) < self.config.min_chunk_size:
                continue
            
            enriched_chunks.append({
                'content': chunk_content,
                'chunk_index': i,
                'metadata': metadata.copy()
            })
        
        return enriched_chunks
    
    def _chunk_cpp(self, content: str) -> List[str]:
        """Chunks C++ files"""
        chunks = []
        
        # Extract complete classes
        class_pattern = r'class\s+\w+[^{]*\{(?:[^{}]|\{[^{}]*\})*\};'
        class_matches = list(re.finditer(class_pattern, content, re.DOTALL))
        
        if class_matches:
            for match in class_matches:
                class_def = match.group(0)
                class_name_match = re.search(r'class\s+(\w+)', class_def)

                if not class_name_match:
                    continue

                class_name = class_name_match.group(1)

                # Find implementations for this class
                impl_pattern = rf'{class_name}::\w+[^{{]*\{{(?:[^{{}}]|\{{[^{{}}]*\}})*\}}'
                implementations = re.findall(impl_pattern, content, re.DOTALL)

                combined = class_def
                if implementations:
                    combined += '\n\n// Implementations:\n' + '\n\n'.join(implementations[:3])

                chunks.append(combined)
        
        # Extract standalone functions
        func_pattern = r'(?:void|int|bool|uint\d+|float|double|std::string)\s+\w+\s*\([^)]*\)\s*\{(?:[^{}]|\{[^{}]*\})*\}'
        func_matches = re.finditer(func_pattern, content, re.DOTALL)
        
        for match in func_matches:
            func_code = match.group(0)
            if len(func_code) > self.config.min_chunk_size:
                chunks.append(func_code)
        
        if not chunks:
            chunks = self._chunk_generic(content)
        
        return chunks
    
    def _chunk_markdown(self, content: str) -> List[str]:
        """Chunks Markdown files by sections"""
        sections = re.split(r'\n(?=#{1,6}\s)', content)
        
        chunks = []
        current_chunk = ""
        
        for section in sections:
            if not section.strip():
                continue
            
            if len(current_chunk) + len(section) > self.config.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = section
            else:
                current_chunk += '\n\n' + section if current_chunk else section
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_config(self, content: str) -> List[str]:
        """Chunks configuration files"""
        chunks = []
        current_section = None
        current_settings = []
        
        for line in content.split('\n'):
            if line.strip().startswith('[') and line.strip().endswith(']'):
                if current_section and current_settings:
                    chunk = f"{current_section}\n" + '\n'.join(current_settings)
                    chunks.append(chunk)
                
                current_section = line.strip()
                current_settings = []
            
            elif line.strip() and not line.strip().startswith('#'):
                current_settings.append(line)
                
                if '=' in line and 'AiPlayerbot' in line:
                    individual_chunk = f"{current_section}\n{line}"
                    chunks.append(individual_chunk)
        
        if current_section and current_settings:
            chunk = f"{current_section}\n" + '\n'.join(current_settings)
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_generic(self, content: str) -> List[str]:
        """Chunks by size with overlap"""
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            
            if current_size + line_size > self.config.chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                
                overlap_lines = []
                overlap_size = 0
                
                for l in reversed(current_chunk):
                    if overlap_size + len(l) < self.config.overlap:
                        overlap_lines.insert(0, l)
                        overlap_size += len(l)
                    else:
                        break
                
                current_chunk = overlap_lines
                current_size = overlap_size
            
            current_chunk.append(line)
            current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
