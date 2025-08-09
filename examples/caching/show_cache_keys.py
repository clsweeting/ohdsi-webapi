"""
Test script to show actual cache keys generated for common operations
"""

from dotenv import load_dotenv

load_dotenv()


def show_cache_keys():
    """Demonstrate actual cache keys used for common operations."""

    from ohdsi_webapi.cache import get_cache_key

    print("🔍 Cache Key Analysis for Common OHDSI WebAPI Operations")
    print("=" * 60)

    # 1. Individual concept lookup
    concept_key = get_cache_key(
        201826, method_name="src.ohdsi_webapi.services.vocabulary.VocabularyService.get_concept"  # Type 2 diabetes concept ID
    )
    print("Individual concept (201826):")
    print(f"  Key: {concept_key}")
    print(f"  Length: {len(concept_key)} chars")
    print()

    # 2. Concept search with different parameters
    search_basic_key = get_cache_key(
        "diabetes", method_name="src.ohdsi_webapi.services.vocabulary.VocabularyService.search", page=1, page_size=20
    )
    print("Basic concept search ('diabetes'):")
    print(f"  Key: {search_basic_key}")
    print()

    # 3. Concept search with filters
    search_filtered_key = get_cache_key(
        "diabetes",
        method_name="src.ohdsi_webapi.services.vocabulary.VocabularyService.search",
        domain_id="Condition",
        standard_concept="S",
        page=1,
        page_size=20,
    )
    print("Filtered concept search ('diabetes', domain='Condition', standard='S'):")
    print(f"  Key: {search_filtered_key}")
    print()

    # 4. List all domains
    domains_key = get_cache_key(method_name="src.ohdsi_webapi.services.vocabulary.VocabularyService.list_domains")
    print("List all domains:")
    print(f"  Key: {domains_key}")
    print()

    # 5. List all concept sets
    concept_sets_key = get_cache_key(method_name="src.ohdsi_webapi.services.concept_sets.ConceptSetService.list")
    print("List all concept sets:")
    print(f"  Key: {concept_sets_key}")
    print()

    # 6. Concept descendants
    descendants_key = get_cache_key(201826, method_name="src.ohdsi_webapi.services.vocabulary.VocabularyService.descendants")
    print("Concept descendants (201826):")
    print(f"  Key: {descendants_key}")
    print()

    # 7. Show how force_refresh affects keys (it doesn't - it's removed before key generation)
    search_force_key = get_cache_key(
        "diabetes",
        method_name="src.ohdsi_webapi.services.vocabulary.VocabularyService.search",
        page=1,
        page_size=20,
        # Note: force_refresh is NOT included because it's popped before key generation
    )
    print("Same search with force_refresh (key identical):")
    print(f"  Key: {search_force_key}")
    print(f"  Same as basic search: {search_basic_key == search_force_key}")
    print()

    # 8. Show how parameter order matters for positional args
    order1_key = get_cache_key("arg1", "arg2", method_name="test.method", param1="value1", param2="value2")
    order2_key = get_cache_key("arg2", "arg1", method_name="test.method", param1="value1", param2="value2")  # Different order
    print("Parameter order sensitivity:")
    print(f"  Key1 (arg1, arg2): {order1_key}")
    print(f"  Key2 (arg2, arg1): {order2_key}")
    print(f"  Different keys: {order1_key != order2_key}")
    print()

    # 9. Show how keyword order doesn't matter (they're sorted)
    kw1_key = get_cache_key("query", method_name="test.method", param_a="value_a", param_b="value_b")
    kw2_key = get_cache_key("query", method_name="test.method", param_b="value_b", param_a="value_a")  # Different order
    print("Keyword parameter order (sorted internally):")
    print(f"  Key1 (a, b): {kw1_key}")
    print(f"  Key2 (b, a): {kw2_key}")
    print(f"  Same keys: {kw1_key == kw2_key}")


if __name__ == "__main__":
    show_cache_keys()
