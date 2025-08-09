"""
Simple cache inspection demo
"""

import os
from dotenv import load_dotenv

load_dotenv()

from ohdsi_webapi import WebApiClient
from ohdsi_webapi.cache import cache_contents, clear_cache

base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
if not base_url:
    print("❌ OHDSI_WEBAPI_BASE_URL not set")
    exit(1)

client = WebApiClient(base_url=base_url)

print("🔍 Cache Inspection Demo")
print("=" * 30)

# Start fresh
clear_cache()
print("Starting with clean cache...")

# Make a few calls
try:
    domains = client.vocabulary.domains()
    print(f"✅ Got {len(domains)} vocabulary domains")
    
    concept = client.vocabulary.get_concept(201826)
    print(f"✅ Got concept: {getattr(concept, 'concept_name', 'Unknown')}")
    
except Exception as e:
    print(f"API call error: {e}")

# Show what's in cache
print("\n📊 Cache contents:")
try:
    contents = cache_contents()
    
    for i, entry in enumerate(contents['entries'], 1):
        print(f"{i}. {entry['key']}")
        print(f"   • Type: {entry['data_type']}")
        print(f"   • Age: {entry['created_ago']:.1f}s")
        print(f"   • TTL: {entry['expires_in']:.0f}s")
        print()
    
    stats = contents['stats']
    print(f"Total: {stats['size']}/{stats['max_size']} entries")
    
except Exception as e:
    print(f"Cache inspection error: {e}")
