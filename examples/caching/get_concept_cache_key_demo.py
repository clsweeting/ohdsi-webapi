"""
Demo showing cache key generation for get_concept() method
"""

from ohdsi_webapi.cache import get_cache_key

def demo_get_concept_cache_key():
    """Show exactly what cache key is used for get_concept()."""
    
    print("🔑 Cache Key for get_concept() Method")
    print("=" * 45)
    
    # This is what the @cached_method decorator does internally
    # for the get_concept() method call
    
    # Example call: client.vocabulary.get_concept(201826)
    # The decorator skips 'self' and uses the remaining args
    
    concept_id = 201826
    method_name = "ohdsi_webapi.services.vocabulary.VocabularyService.get_concept"
    
    # This is the actual cache key generation
    cache_key = get_cache_key(
        concept_id,  # args[1:] (skipping 'self')
        method_name=method_name,
        # No kwargs in this case
    )
    
    print(f"Method call: client.vocabulary.get_concept({concept_id})")
    print(f"Full method name: {method_name}")
    print(f"Generated cache key: {cache_key}")
    print()
    
    # Show a few more examples
    examples = [
        {
            "call": "get_concept(201826)",
            "args": [201826],
            "kwargs": {}
        },
        {
            "call": "get_concept(316866)", 
            "args": [316866],
            "kwargs": {}
        },
        {
            "call": "get_concept(201826, force_refresh=True)",
            "args": [201826],
            "kwargs": {"force_refresh": True}  # This would be popped before cache key gen
        }
    ]
    
    print("📋 More Examples:")
    print("-" * 20)
    
    for example in examples:
        # Note: force_refresh is popped before cache key generation
        filtered_kwargs = {k: v for k, v in example["kwargs"].items() if k != "force_refresh"}
        
        key = get_cache_key(
            *example["args"],
            method_name=method_name,
            **filtered_kwargs
        )
        print(f"Call: {example['call']}")
        print(f"Key:  {key}")
        print()

if __name__ == "__main__":
    demo_get_concept_cache_key()
