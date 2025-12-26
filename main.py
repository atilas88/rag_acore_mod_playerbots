#!/usr/bin/env python3
# main.py
"""
Main application - Interactive RAG interface
"""

import os
import sys
from pathlib import Path
from src.config import Config
from src.pipeline import RAGPipeline
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def print_header():
    """Prints application header"""
    print("\n" + "="*70)
    print("RAG AZEROTHCORE - Intelligent Query System")
    print("Documentation: AzerothCore + mod-playerbots")
    print("="*70 + "\n")

def print_help():
    """Prints available commands"""
    print("\nAVAILABLE COMMANDS:")
    print("  /help     - Show this help")
    print("  /stats    - Show system statistics")
    print("  /cache    - Show cache statistics")
    print("  /clear    - Clear cache")
    print("  /filters  - Configure search filters")
    print("  /exit     - Exit the program")
    print()

def configure_filters():
    """Allows interactive filter configuration"""
    print("\nFILTER CONFIGURATION:")
    print("Press Enter to skip any filter\n")

    filters = {}

    module = input("Module (playerbots/core): ").strip()
    if module:
        filters['module'] = module

    category = input("Category (combat/movement/ai/config/etc): ").strip()
    if category:
        filters['category'] = category

    file_type = input("File type (cpp/h/md/conf): ").strip()
    if file_type:
        filters['type'] = file_type

    return filters if filters else None

def main():
    config_path = "./configs/config.yaml"
    
    if os.path.exists(config_path):
        config = Config.from_yaml(config_path)
        logger.info(f"✅ Configuration loaded from {config_path}")
    else:
        config = Config()
        logger.info("⚠️  Using default configuration")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY is not configured")
        print("   Set it with: export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)
    
    print_header()
    print("⏳ Initializing system...")

    pipeline = RAGPipeline(config, api_key)

    if os.path.exists(config.embeddings_path):
        print("📂 Loading existing index...")
        if not pipeline.load_index():
            print("❌ Error loading index")
            print("   Run: python scripts/build_index.py")
            sys.exit(1)
    else:
        print("⚠️  Existing index not found")
        print("   Run first: python scripts/build_index.py")
        sys.exit(1)

    print("✅ System ready!")
    print_help()
    
    current_filters = None
    
    while True:
        try:
            filter_str = f" [Filters: {current_filters}]" if current_filters else ""
            question = input(f"\n💬 Your question{filter_str}: ").strip()
            
            if not question:
                continue
            
            if question.startswith('/'):
                command = question.lower()
                
                if command == '/help':
                    print_help()
                
                elif command == '/stats':
                    stats = pipeline.get_statistics()
                    print("\n📊 SYSTEM STATISTICS:")
                    print(f"\nVector Store:")
                    print(f"  Total chunks: {stats['vector_store']['total_chunks']}")
                    print(f"  By module: {stats['vector_store']['by_module']}")
                    print(f"  By category: {stats['vector_store']['by_category']}")

                    if 'query_stats' in stats and stats['query_stats']:
                        qs = stats['query_stats']
                        print(f"\nQueries (last {qs['total_queries']}):")
                        print(f"  Average time: {qs['avg_response_time']:.2f}s")
                        print(f"  Cache hit rate: {qs['cache_hit_rate']*100:.1f}%")
                        print(f"  Error rate: {qs['error_rate']*100:.1f}%")

                    if 'cache' in stats:
                        print(f"\nCache:")
                        print(f"  Cached queries: {stats['cache']['total_cached_queries']}")
                        print(f"  Size: {stats['cache']['cache_size_mb']:.2f} MB")
                
                elif command == '/cache':
                    if pipeline.cache:
                        cache_stats = pipeline.cache.get_stats()
                        print("\n💾 CACHE STATISTICS:")
                        print(f"  Cached queries: {cache_stats['total_cached_queries']}")
                        print(f"  Total size: {cache_stats['cache_size_mb']:.2f} MB")
                        print(f"  Directory: {cache_stats['cache_dir']}")
                    else:
                        print("⚠️  Cache disabled")
                
                elif command == '/clear':
                    if pipeline.cache:
                        confirm = input("Clear all cache? (y/n): ").lower()
                        if confirm == 'y':
                            pipeline.cache.clear_all()
                            print("✅ Cache cleared")
                    else:
                        print("⚠️  Cache disabled")
                
                elif command == '/filters':
                    current_filters = configure_filters()
                    if current_filters:
                        print(f"✅ Filters configured: {current_filters}")
                    else:
                        print("✅ Filters removed")
                
                elif command in ['/exit', '/quit']:
                    print("\n👋 See you later!")
                    break

                else:
                    print(f"❌ Unknown command: {command}")
                    print("   Use /help to see available commands")
                
                continue
            
            print("\n🔍 Searching for information...")

            try:
                response = pipeline.query(
                    question,
                    filters=current_filters,
                    use_cache=True
                )

                print("\n" + "="*70)
                print("💡 RESPONSE:")
                print("="*70)
                print(f"\n{response}\n")
                print("="*70)

            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                logger.error(f"Error processing query: {str(e)}", exc_info=True)
        
        except KeyboardInterrupt:
            print("\n\n👋 See you later!")
            break

        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
