"""
Detailed breakdown of cache key generation process
"""

import hashlib

def trace_cache_key_generation():
    """Show step-by-step how cache keys are generated."""
    
    print("🔍 Step-by-Step Cache Key Generation")
    print("=" * 50)
    
    # Example: Individual concept lookup for Type 2 diabetes (concept ID 201826)
    print("Example: Get concept 201826 (Type 2 diabetes)")
    print()
    
    # Step 1: Gather the inputs
    print("Step 1: Method call inputs")
    method_name = "ohdsi_webapi.services.vocabulary.VocabularyService.get_concept"
    concept_id = 201826
    force_refresh = False  # This will be removed
    
    print(f"  Method: {method_name}")
    print(f"  Positional args: [{concept_id}]")
    print(f"  Keyword args: {{force_refresh: {force_refresh}}}")
    print()
    
    # Step 2: Process arguments (as done in cached_method decorator)
    print("Step 2: Argument processing in @cached_method decorator")
    args = (concept_id,)  # Skip 'self' parameter (args[1:])
    kwargs = {}  # force_refresh is popped out before key generation
    
    print(f"  Args after removing 'self': {args}")
    print(f"  Kwargs after removing 'force_refresh': {kwargs}")
    print()
    
    # Step 3: Build key parts (as done in get_cache_key)
    print("Step 3: Build key components")
    key_parts = [method_name]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    
    print(f"  Key parts list: {key_parts}")
    print()
    
    # Step 4: Join into string
    print("Step 4: Join components with '|' separator")
    key_string = "|".join(key_parts)
    print(f"  Raw key string: '{key_string}'")
    print(f"  String length: {len(key_string)} characters")
    print()
    
    # Step 5: MD5 hash
    print("Step 5: Generate MD5 hash")
    encoded_string = key_string.encode()
    print(f"  UTF-8 encoded bytes: {encoded_string}")
    print(f"  Byte length: {len(encoded_string)}")
    
    hash_object = hashlib.md5(encoded_string)
    hex_hash = hash_object.hexdigest()
    
    print(f"  MD5 hash object: {hash_object}")
    print(f"  Final cache key: {hex_hash}")
    print(f"  Key length: {len(hex_hash)} characters")
    print()
    
    # Verify this matches what get_cache_key produces
    from ohdsi_webapi.cache import get_cache_key
    actual_key = get_cache_key(
        201826,
        method_name="ohdsi_webapi.services.vocabulary.VocabularyService.get_concept"
    )
    
    print("Step 6: Verification")
    print(f"  Our calculated key: {hex_hash}")
    print(f"  get_cache_key result: {actual_key}")
    print(f"  Keys match: {hex_hash == actual_key}")
    print()
    
    # Show how different inputs produce different keys
    print("🔍 How Different Inputs Change the Key")
    print("=" * 50)
    
    examples = [
        # Different concept ID
        {
            "description": "Different concept (316866 - Hypertension)",
            "args": (316866,),
            "kwargs": {},
            "method": "ohdsi_webapi.services.vocabulary.VocabularyService.get_concept"
        },
        # Same concept, different method
        {
            "description": "Same concept, different method (descendants)",
            "args": (201826,),
            "kwargs": {},
            "method": "ohdsi_webapi.services.vocabulary.VocabularyService.descendants"
        },
        # Concept search with parameters
        {
            "description": "Concept search with parameters",
            "args": ("diabetes",),
            "kwargs": {"page": 1, "page_size": 20},
            "method": "ohdsi_webapi.services.vocabulary.VocabularyService.search"
        },
        # No arguments (like list domains)
        {
            "description": "No arguments (list domains)",
            "args": (),
            "kwargs": {},
            "method": "ohdsi_webapi.services.vocabulary.VocabularyService.list_domains"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['description']}")
        
        # Build key string
        key_parts = [example['method']]
        key_parts.extend(str(arg) for arg in example['args'])
        key_parts.extend(f"{k}={v}" for k, v in sorted(example['kwargs'].items()))
        key_string = "|".join(key_parts)
        
        # Generate hash
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        
        print(f"   Raw string: '{key_string}'")
        print(f"   Cache key:  {cache_key}")
        print()

if __name__ == "__main__":
    trace_cache_key_generation()
