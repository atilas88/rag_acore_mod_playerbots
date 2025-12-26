#!/usr/bin/env python3
# scripts/evaluate.py
"""
Script to evaluate the RAG system quality
"""
import os
import sys
import json
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.pipeline import RAGPipeline

def load_test_queries(filepath: str = "./tests/test_queries.json") -> List[Dict]:
    """Load test queries"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['test_queries']

def evaluate_retrieval(pipeline: RAGPipeline, test_queries: List[Dict]) -> Dict:
    """Evaluate retrieval quality"""
    results = {
        'total_queries': len(test_queries),
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    for test in test_queries:
        query = test['query']
        expected_keywords = test['expected_keywords']
        expected_files = test.get('expected_files', [])
        
        print(f"\n🔍 Evaluating: {query}")
        
        chunks = pipeline.get_relevant_chunks(query, k=5)
        
        all_content = ' '.join([
            chunk['chunk']['content'].lower() 
            for chunk in chunks
        ])
        
        keywords_found = [
            kw for kw in expected_keywords 
            if kw.lower() in all_content
        ]
        
        files_found = [
            ef for ef in expected_files
            if any(ef in chunk['metadata']['filename'] for chunk in chunks)
        ]
        
        keyword_score = len(keywords_found) / len(expected_keywords) if expected_keywords else 0
        file_score = len(files_found) / len(expected_files) if expected_files else 1
        
        passed = keyword_score >= 0.5 and file_score >= 0.5
        
        if passed:
            results['passed'] += 1
            status = "✅ PASS"
        else:
            results['failed'] += 1
            status = "❌ FAIL"
        
        print(f"   {status}")
        print(f"   Keywords: {len(keywords_found)}/{len(expected_keywords)}")
        print(f"   Files: {len(files_found)}/{len(expected_files)}")
        
        results['details'].append({
            'query': query,
            'passed': passed,
            'keyword_score': keyword_score,
            'file_score': file_score,
            'keywords_found': keywords_found,
            'files_found': files_found
        })
    
    return results

def main():
    print("\n" + "="*70)
    print("RAG EVALUATION - AZEROTHCORE")
    print("="*70 + "\n")
    
    config = Config.from_yaml("./configs/config.yaml") if os.path.exists("./configs/config.yaml") else Config()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not configured")
        sys.exit(1)
    
    pipeline = RAGPipeline(config, api_key)
    
    if not pipeline.load_index():
        print("❌ Could not load index")
        print("   Run build_index.py first")
        sys.exit(1)
    
    test_queries = load_test_queries()
    print(f"📋 Loaded {len(test_queries)} test queries\n")
    
    print("="*70)
    print("RETRIEVAL EVALUATION")
    print("="*70)
    
    retrieval_results = evaluate_retrieval(pipeline, test_queries)
    
    print("\n📊 RESULTS:")
    print(f"   Total: {retrieval_results['total_queries']}")
    print(f"   Passed: {retrieval_results['passed']} ({retrieval_results['passed']/retrieval_results['total_queries']*100:.1f}%)")
    print(f"   Failed: {retrieval_results['failed']} ({retrieval_results['failed']/retrieval_results['total_queries']*100:.1f}%)")
    
    output_file = "./data/evaluation_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'retrieval': retrieval_results}, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Results saved to: {output_file}")

if __name__ == "__main__":
    main()
