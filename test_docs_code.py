#!/usr/bin/env python3
"""
Test script to validate all code samples in documentation work with Atlas demo WebAPI.
"""

import sys
import traceback

from ohdsi_webapi import WebApiClient


def test_basic_connection():
    """Test basic connection to Atlas demo."""
    print("=== Testing Basic Connection ===")
    try:
        client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")
        info = client.info()
        print(f"✓ Connected to WebAPI version: {info.version}")
        return client
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None


def test_sources():
    """Test sources functionality."""
    print("\n=== Testing Sources ===")
    try:
        client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")
        sources = client.source.sources()  # Updated to use new API
        print(f"✓ Retrieved {len(sources)} sources")
        if sources:
            src = sources[0]
            print(f"✓ First source: {src.source_key} - {src.source_name}")
        return True
    except Exception as e:
        print(f"✗ Sources failed: {e}")
        traceback.print_exc()
        return False


def test_vocabulary_basic(client):
    """Test basic vocabulary operations."""
    print("\n=== Testing Vocabulary - Basic ===")
    try:
        # Test single concept
        concept = client.vocabulary.concept(201826)  # Type 2 diabetes
        print(f"✓ Retrieved concept: {concept.concept_name}")

        # Test domains
        domains = client.vocabulary.domains()
        print(f"✓ Retrieved {len(domains)} domains")

        # Test vocabularies
        vocabularies = client.vocabulary.vocabularies()
        print(f"✓ Retrieved {len(vocabularies)} vocabularies")

        return True
    except Exception as e:
        print(f"✗ Vocabulary basic failed: {e}")
        traceback.print_exc()
        return False


def test_vocabulary_search(client):
    """Test vocabulary search functionality."""
    print("\n=== Testing Vocabulary - Search ===")
    try:
        # Test search
        results = client.vocabulary.search("diabetes", domain_id="Condition", page_size=5)
        print(f"✓ Search returned {len(results)} results")

        # Test concepts (our simplified version)
        concept_ids = [201826, 1503297]  # diabetes, metformin
        concepts = client.vocabulary.concepts(concept_ids)
        print(f"✓ Retrieved {len(concepts)} concepts via concepts() method")

        return True
    except Exception as e:
        print(f"✗ Vocabulary search failed: {e}")
        traceback.print_exc()
        return False


def test_concept_sets(client):
    """Test concept sets functionality."""
    print("\n=== Testing Concept Sets ===")
    try:
        # Test list concept sets
        concept_sets = client.conceptset()
        print(f"✓ Retrieved {len(concept_sets)} concept sets")

        if concept_sets:
            # Test get specific concept set
            cs = client.conceptset(concept_sets[0].id)
            print(f"✓ Retrieved concept set: {cs.name}")

            # Test concept set expression
            expr = client.conceptset_expression(concept_sets[0].id)
            print(f"✓ Retrieved concept set expression with {len(expr.get('items', []))} items")

            # Test concept set items
            items = client.conceptset_items(concept_sets[0].id)
            print(f"✓ Retrieved {len(items)} concept set items")

        return True
    except Exception as e:
        print(f"✗ Concept sets failed: {e}")
        traceback.print_exc()
        return False


def test_cohorts_basic(client):
    """Test basic cohorts functionality."""
    print("\n=== Testing Cohorts - Basic ===")
    try:
        # Test list cohorts
        cohorts = client.cohortdefinition()
        print(f"✓ Retrieved {len(cohorts)} cohort definitions")

        if cohorts:
            # Test get specific cohort
            cohort = client.cohortdefinition(cohorts[0].id)
            print(f"✓ Retrieved cohort: {cohort.name}")

        return True
    except Exception as e:
        print(f"✗ Cohorts basic failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Testing documentation code samples against Atlas demo WebAPI")
    print("=" * 60)

    # Test connection first
    client = test_basic_connection()
    if not client:
        print("Cannot proceed without connection")
        sys.exit(1)

    # Run all tests
    tests = [
        test_sources,
        test_vocabulary_basic,
        test_vocabulary_search,
        test_concept_sets,
        test_cohorts_basic,
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func(client):
                passed += 1
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
            traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Documentation code samples are working.")
        client.close()
        sys.exit(0)
    else:
        print("❌ Some tests failed. Documentation needs fixes.")
        client.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
