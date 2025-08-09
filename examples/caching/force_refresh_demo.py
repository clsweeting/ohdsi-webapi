"""
Demo of how force_refresh works in get_concept method
"""

import os

from dotenv import load_dotenv

load_dotenv()


def demo_force_refresh():
    """Demonstrate how force_refresh bypasses the cache."""

    import time

    from ohdsi_webapi import WebApiClient
    from ohdsi_webapi.cache import cache_contents, clear_cache

    base_url = os.getenv("OHDSI_WEBAPI_BASE_URL")
    if not base_url:
        print("❌ OHDSI_WEBAPI_BASE_URL not set")
        return

    client = WebApiClient(base_url=base_url)

    print("🔄 Force Refresh Demo")
    print("=" * 30)

    # Start with clean cache
    clear_cache()
    print("1. Starting with clean cache")

    try:
        # First call - will populate cache
        print("\n2. First call (cache miss):")
        start = time.time()
        concept1 = client.vocabulary.get_concept(201826)
        time1 = time.time() - start
        print(f"   ✅ Retrieved concept in {time1:.3f}s")

        # Check cache
        contents = cache_contents()
        print(f"   📊 Cache now has {contents['stats']['size']} entry")
        if contents["entries"]:
            print(f"   🔑 Key: {contents['entries'][0]['key']}")

        # Second call - should hit cache
        print("\n3. Second call (cache hit):")
        start = time.time()
        client.vocabulary.get_concept(201826)
        time2 = time.time() - start
        print(f"   ⚡ Retrieved concept in {time2:.3f}s (from cache)")
        print(f"   🚀 Speed improvement: {time1/time2:.1f}x faster")

        # Third call with force_refresh=True
        print("\n4. Third call with force_refresh=True:")
        start = time.time()
        concept3 = client.vocabulary.get_concept(201826, force_refresh=True)
        time3 = time.time() - start
        print(f"   🔄 Retrieved concept in {time3:.3f}s (bypassed cache)")
        print("   📡 Fresh API call (similar timing to first call)")

        # Check cache again - should still have only 1 entry
        contents = cache_contents()
        print("\n5. Cache status after force_refresh:")
        print(f"   📊 Cache still has {contents['stats']['size']} entry")
        print("   ℹ️  force_refresh bypassed cache completely")

        # Verify all concepts are the same
        print("\n6. Data consistency:")
        print(f"   Concept names match: {getattr(concept1, 'concept_name', 'N/A') == getattr(concept3, 'concept_name', 'N/A')}")

    except Exception as e:
        print(f"Error: {e}")


def explain_force_refresh_mechanism():
    """Explain the internal mechanics of force_refresh."""

    print("\n🔧 How force_refresh Works Internally")
    print("=" * 40)

    print(
        """
The @cached_method decorator handles force_refresh as follows:

1. PARAMETER EXTRACTION:
   def wrapper(*args, **kwargs):
       force_refresh = kwargs.pop('force_refresh', False)
   
   • Extracts force_refresh from kwargs
   • Removes it so it doesn't affect cache key generation
   • Defaults to False if not provided

2. CACHE BYPASS CHECK:
   if not cache_enabled or force_refresh:
       return func(*args, **kwargs)
   
   • If force_refresh=True, immediately calls the original function
   • Completely bypasses all cache logic (no read, no write)
   • Returns fresh data directly from API

3. NORMAL CACHE FLOW (when force_refresh=False):
   cache_key = get_cache_key(*args[1:], method_name=..., **kwargs)
   cached_result = _global_cache.get(cache_key)
   if cached_result is not None:
       return cached_result
   
   • Generates cache key (excluding force_refresh)
   • Checks cache for existing entry
   • Returns cached data if found and not expired
   
4. CACHE MISS HANDLING:
   result = func(*args, **kwargs)
   _global_cache.set(cache_key, result, ttl_seconds)
   return result
   
   • Calls original function to get fresh data
   • Stores result in cache for future use
   • Returns the fresh data

Key Points:
• force_refresh=True completely bypasses the cache
• No cache read, no cache write when force_refresh=True
• Cache key generation excludes force_refresh parameter
• Ensures consistent cache keys regardless of force_refresh value
"""
    )


if __name__ == "__main__":
    explain_force_refresh_mechanism()
    demo_force_refresh()
