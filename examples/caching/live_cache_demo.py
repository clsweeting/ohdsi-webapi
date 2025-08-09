"""
Live cache behavior demonstration with actual WebAPI calls
"""

import os
from dotenv import load_dotenv

load_dotenv()

def demonstrate_live_caching():
    """Show actual cache behavior with live WebAPI calls."""
    
    from ohdsi_webapi import WebApiClient
    from ohdsi_webapi.cache import cache_stats, clear_cache
    
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ OHDSI_WEBAPI_BASE_URL not set")
        return
    
    client = WebApiClient(base_url=base_url)
    
    print("🔍 Live Cache Behavior Demonstration")
    print("=" * 50)
    
    # Start with clean cache
    clear_cache()
    print("1. Starting with clean cache:")
    print(f"   {cache_stats()}")
    print()
    
    # Test concept lookup caching
    print("2. First call to get concept 201826 (Type 2 diabetes):")
    try:
        concept = client.vocabulary.get_concept(201826)
        print(f"   Got concept: {concept.conceptName}")
        print(f"   Cache after: {cache_stats()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Second call should hit cache
    print("3. Second call to same concept (should hit cache):")
    try:
        concept = client.vocabulary.get_concept(201826)
        print(f"   Got concept: {concept.conceptName}")
        print(f"   Cache after: {cache_stats()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test domains caching
    print("4. First call to list domains:")
    try:
        domains = client.vocabulary.domains()
        print(f"   Got {len(domains)} domains")
        print(f"   Cache after: {cache_stats()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test force refresh
    print("5. Force refresh of concept (bypasses cache):")
    try:
        concept = client.vocabulary.get_concept(201826, force_refresh=True)
        print(f"   Got concept: {concept.conceptName}")
        print(f"   Cache after: {cache_stats()}")  # Size should stay same
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test different concept
    print("6. Get different concept (new cache entry):")
    try:
        concept = client.vocabulary.get_concept(316866)  # Hypertension
        print(f"   Got concept: {concept.conceptName}")
        print(f"   Cache after: {cache_stats()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Show cache keys in action
    print("7. Actual cache keys being used:")
    from ohdsi_webapi.cache import get_cache_key
    
    # Show key for Type 2 diabetes concept
    key1 = get_cache_key(
        201826,
        method_name="ohdsi_webapi.services.vocabulary.VocabularyService.get_concept"
    )
    print(f"   Type 2 diabetes (201826): {key1}")
    
    # Show key for hypertension concept  
    key2 = get_cache_key(
        316866,
        method_name="ohdsi_webapi.services.vocabulary.VocabularyService.get_concept"
    )
    print(f"   Hypertension (316866): {key2}")
    
    # Show key for domains
    key3 = get_cache_key(
        method_name="ohdsi_webapi.services.vocabulary.VocabularyService.list_domains"
    )
    print(f"   List domains: {key3}")
    print()
    
    print("8. Final cache state:")
    print(f"   {cache_stats()}")

if __name__ == "__main__":
    demonstrate_live_caching()
