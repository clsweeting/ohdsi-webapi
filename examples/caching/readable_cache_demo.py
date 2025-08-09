"""
Demo of new human-readable cache keys
"""

import os
from dotenv import load_dotenv

load_dotenv()

def demo_readable_cache_keys():
    """Show the new human-readable cache keys in action."""
    
    from ohdsi_webapi import WebApiClient
    from ohdsi_webapi.cache import cache_stats, cache_contents, clear_cache
    
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ OHDSI_WEBAPI_BASE_URL not set")
        return
    
    client = WebApiClient(base_url=base_url)
    
    print("🎯 Human-Readable Cache Keys Demo")
    print("=" * 50)
    
    # Start with clean cache
    clear_cache()
    print("1. Starting with clean cache")
    print()
    
    # Make some API calls to populate cache
    print("2. Making API calls to populate cache...")
    
    try:
        # Individual concept lookup
        print("   • Getting concept 201826 (Type 2 diabetes)")
        concept = client.vocabulary.get_concept(201826)
        
        # Another concept
        print("   • Getting concept 316866 (Hypertension)")
        concept2 = client.vocabulary.get_concept(316866)
        
        # List domains
        print("   • Listing vocabulary domains")
        domains = client.vocabulary.domains()
        
        # Concept search
        print("   • Searching for 'diabetes' concepts")
        search_results = client.vocabulary.search("diabetes", page_size=5)
        
    except Exception as e:
        print(f"   Error during API calls: {e}")
    
    print()
    
    # Show cache contents with readable keys
    print("3. Cache contents with human-readable keys:")
    print("-" * 40)
    
    try:
        contents = cache_contents()
        
        for entry in contents['entries']:
            print(f"🔑 {entry['key']}")
            print(f"   Created {entry['created_ago']}s ago, expires in {entry['expires_in']}s")
            print(f"   Data: {entry['data_type']}")
            print()
        
        stats = contents['stats']
        print(f"📊 Total cached: {stats['size']}/{stats['max_size']} entries")
        
    except Exception as e:
        print(f"Error showing cache contents: {e}")

def demo_key_generation():
    """Show how the new cache keys are generated."""
    
    from ohdsi_webapi.cache import get_cache_key
    
    print("\n🔧 Cache Key Generation Examples")
    print("=" * 50)
    
    examples = [
        {
            "description": "Individual concept lookup",
            "call": "client.vocabulary.get_concept(201826)",
            "key": get_cache_key(201826, method_name="VocabularyService.get_concept")
        },
        {
            "description": "Basic concept search", 
            "call": 'client.vocabulary.search("diabetes")',
            "key": get_cache_key("diabetes", method_name="VocabularyService.search", page=1, page_size=20)
        },
        {
            "description": "Filtered concept search",
            "call": 'client.vocabulary.search("diabetes", domain_id="Condition")',
            "key": get_cache_key("diabetes", method_name="VocabularyService.search", domain_id="Condition", page=1, page_size=20)
        },
        {
            "description": "List domains (no args)",
            "call": "client.vocabulary.domains()",
            "key": get_cache_key(method_name="VocabularyService.list_domains")
        },
        {
            "description": "Concept descendants",
            "call": "client.vocabulary.descendants(201826)",
            "key": get_cache_key(201826, method_name="VocabularyService.descendants")
        },
        {
            "description": "Concept set lookup",
            "call": "client.concept_sets.get(42)",
            "key": get_cache_key(42, method_name="ConceptSetService.get")
        }
    ]
    
    for example in examples:
        print(f"📞 {example['description']}")
        print(f"   API call: {example['call']}")
        print(f"   Cache key: {example['key']}")
        print()

if __name__ == "__main__":
    demo_key_generation()
    demo_readable_cache_keys()
