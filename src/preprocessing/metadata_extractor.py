# src/preprocessing/metadata_extractor.py
"""
Extracts useful metadata from documents
"""

import re
from pathlib import Path
from typing import Dict, List

class MetadataExtractor:   
    
    def __init__(self):
        self.category_keywords = {
            'combat': ['combat', 'attack', 'spell', 'damage', 'heal', 'threat'],
            'movement': ['move', 'follow', 'position', 'teleport', 'navigation'],
            'ai': ['ai', 'decision', 'behavior', 'strategy', 'brain', 'engine', 'factory'],
            'config': ['config', 'setting', 'option', 'parameter'],
            'database': ['sql', 'table', 'query', 'insert', 'select', 'update'],
            'inventory': ['inventory', 'item', 'equipment', 'bag', 'loot'],
            'social': ['guild', 'group', 'party', 'raid', 'chat', 'whisper'],
            'quest': ['quest', 'objective', 'reward', 'questgiver'],
        }
    
    def extract(self, content: str, filepath: str) -> Dict:
        
        path_parts = Path(filepath).parts
        filename = Path(filepath).name
        file_ext = Path(filepath).suffix[1:]
        
        metadata = {
            'filename': filename,
            'filepath': filepath,
            'type': file_ext,
            'module': self._detect_module(path_parts),
            'subsystem': self._detect_subsystem(path_parts),
            'category': self._detect_category(content),
            'tags': self._extract_tags(content, file_ext),
            'has_config': self._has_config_info(content),
            'has_example': self._has_code_example(content),
            'has_sql': 'sql' in content.lower() or file_ext == 'sql',
            'complexity': self._estimate_complexity(content),
            'language': self._detect_language(file_ext),
        }
        
        return metadata
    
    def _detect_module(self, path_parts: tuple) -> str:
        
        if 'mod-playerbots' in path_parts:
            return 'playerbots'
        elif 'modules' in path_parts:
            idx = path_parts.index('modules')
            if idx + 1 < len(path_parts):
                return path_parts[idx + 1]
        return 'core'
    
    def _detect_subsystem(self, path_parts: tuple) -> str:
       
        subsystems = [
            'strategy', 
            'actions', 
            'triggers', 
            'values', 
            'ai', 
            'factory',
            'dungeons',
            'generic',
            'raids',
            'rpg',
            'deathknight',
            'druid',
            'hunter',
            'mage',
            'paladin',
            'priest',
            'rogue',
            'shaman',
            'warlock',
            'warrior',
            ]
        for part in path_parts:
            if part in subsystems:
                return part
        return 'general'
    
    def _detect_category(self, content: str) -> str:
        
        content_lower = content.lower()
        scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(
                content_lower.count(keyword) 
                for keyword in keywords
            )
            scores[category] = score
        
        if not scores or max(scores.values()) == 0:
            return 'general'
        
        return max(scores, key=lambda k: scores[k])
    
    def _extract_tags(self, content: str, file_type: str) -> List[str]:
        
        tags = set()
        tags.add(file_type)
        
        if file_type in ['cpp', 'h']:
            class_matches = re.findall(r'class\s+(\w+)', content)
            tags.update(class_matches[:5])
        
        if 'aiplayerbot' in content.lower():
            tags.add('playerbot-config')
        
        if 'command' in content.lower():
            tags.add('commands')
        
        return list(tags)
    
    def _has_config_info(self, content: str) -> bool:
       
        config_indicators = [
            'config', 'setting', '.conf', 'parameter',
            'AiPlayerbot.', 'sConfigMgr'
        ]
        return any(indicator in content for indicator in config_indicators)
    
    def _has_code_example(self, content: str) -> bool:
        
        code_patterns = [
            r'```\w+',
            r'class\s+\w+',
            r'void\s+\w+\s*\(',
        ]
        return any(re.search(pattern, content) for pattern in code_patterns)
    
    def _estimate_complexity(self, content: str) -> str:
        
        lines = len(content.split('\n'))
        
        if lines < 50:
            return 'simple'
        elif lines < 200:
            return 'medium'
        else:
            return 'complex'
    
    def _detect_language(self, file_ext: str) -> str:
        
        language_map = {
            'cpp': 'c++',
            'h': 'c++',
            'md': 'markdown',
            'conf': 'config',
            'sql': 'sql',
            'lua': 'lua',
        }
        return language_map.get(file_ext, 'text')
