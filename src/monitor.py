# src/monitor.py
"""
Monitoring and logging for the RAG system
"""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import time

class RAGMonitor:
    """Monitoring and logging for the RAG system"""
    
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.log_dir / "metrics.jsonl"
        self.queries_file = self.log_dir / "queries.jsonl"
        
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging"""
        log_file = self.log_dir / "rag.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def log_query(
        self, 
        query: str, 
        num_chunks: int,
        response_time: float,
        cache_hit: bool = False,
        error: str | None = None
    ):
        """Log a query"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'num_chunks_retrieved': num_chunks,
            'response_time_seconds': response_time,
            'cache_hit': cache_hit,
            'error': error
        }
        
        self._append_jsonl(self.queries_file, entry)
    
    def log_metrics(self, metrics: Dict):
        """Log system metrics"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            **metrics
        }
        
        self._append_jsonl(self.metrics_file, entry)
    
    def _append_jsonl(self, filepath: Path, data: Dict):
        """Append line to JSONL file"""
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def get_query_stats(self, last_n: int = 100) -> Dict:
        """Get statistics from recent queries"""
        if not self.queries_file.exists():
            return {}
        
        queries = []
        with open(self.queries_file, 'r', encoding='utf-8') as f:
            for line in f:
                queries.append(json.loads(line))
        
        recent_queries = queries[-last_n:]
        
        if not recent_queries:
            return {}
        
        response_times = [q['response_time_seconds'] for q in recent_queries if not q.get('error')]
        cache_hits = sum(1 for q in recent_queries if q.get('cache_hit'))
        errors = sum(1 for q in recent_queries if q.get('error'))
        
        stats = {
            'total_queries': len(recent_queries),
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'cache_hit_rate': cache_hits / len(recent_queries),
            'error_rate': errors / len(recent_queries)
        }
        
        return stats
    
    def analyze_common_queries(self, min_count: int = 3) -> List[Dict]:
        """Analyze most common queries"""
        if not self.queries_file.exists():
            return []
        
        query_counts = {}
        
        with open(self.queries_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                query = data['query'].lower().strip()
                query_counts[query] = query_counts.get(query, 0) + 1
        
        common_queries = [
            {'query': q, 'count': c}
            for q, c in query_counts.items()
            if c >= min_count
        ]
        
        common_queries.sort(key=lambda x: x['count'], reverse=True)
        
        return common_queries

