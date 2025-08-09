"""
Quick demo of cache_contents() function
"""

import os
from dotenv import load_dotenv

load_dotenv()

def quick_cache_demo():
    """Quick demo of cache inspection."""
    
    from ohdsi_webapi import WebApiClient
    from ohdsi_webapi.cache import cache_contents, clear_cache
    
    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ OHDSI_WEBAPI_BASE_URL not set")
        return
    
    client = WebApiClient(base_url=base_url)
    
    print("🔍 Cache Contents Demo")
    print("=" * 30)
    
    # Start fresh
    clear_cache()
    
    # Make a few calls
    try:
        print("Making some API calls...")
        domains = client.vocabulary.domains()
        concept = client.vocabulary.get_concept(201826)
        print(f"Found {len(domains)} domains and got concept {concept.concept_id}")
        
        # Show cache contents
        contents = cache_contents()
        print(f"\n📊 Cache now has {contents['stats']['size']} entries:")
        
        for entry in contents['entries']:
            print(f"  • {entry['key']}")
            print(f"    {entry['data_type']}, expires in {entry['expires_in']}s")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_cache_demo()
