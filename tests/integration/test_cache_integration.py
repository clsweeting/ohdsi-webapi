"""
Integration tests for caching with actual service methods.
"""

import time
from unittest.mock import patch

import httpx
import pytest
import respx
from ohdsi_webapi import WebApiClient
from ohdsi_webapi.cache import cache_contents, cache_stats, clear_cache


class TestServiceCacheIntegration:
    """Test caching integration with actual service methods."""

    def setup_method(self):
        """Setup for each test."""
        clear_cache()
        self.base_url = "https://test.ohdsi.org/WebAPI"
        self.client = WebApiClient(base_url=self.base_url)

    @respx.mock
    def test_vocabulary_get_concept_caching(self):
        """Test that vocabulary.get_concept properly caches results."""

        # Mock API response
        concept_data = {
            "conceptId": 201826,
            "conceptName": "Type 2 diabetes mellitus",
            "vocabularyId": "SNOMED",
            "conceptCode": "44054006",
            "conceptClassId": "Clinical Finding",
            "standardConcept": "S",
            "domainId": "Condition",
            "validStartDate": "1970-01-01",
            "validEndDate": "2099-12-31",
            "invalidReason": None,
        }

        # Setup mock to track call count
        call_count = 0

        def mock_response(request):
            nonlocal call_count
            call_count += 1
            return httpx.Response(200, json=concept_data)

        respx.get(f"{self.base_url}/vocabulary/concept/201826").mock(side_effect=mock_response)

        # First call - should hit API and cache result
        concept1 = self.client.vocabulary.get_concept(201826)
        assert call_count == 1
        assert concept1.conceptId == 201826
        assert concept1.conceptName == "Type 2 diabetes mellitus"

        # Second call - should use cache
        concept2 = self.client.vocabulary.get_concept(201826)
        assert call_count == 1  # No additional API call
        assert concept2.conceptId == concept1.conceptId

        # Verify cache contents
        contents = cache_contents()
        assert len(contents["entries"]) == 1
        assert contents["entries"][0]["key"] == "VocabularyService.get_concept(201826)"
        assert "Concept" in contents["entries"][0]["data_type"]

    @respx.mock
    def test_vocabulary_get_concept_force_refresh(self):
        """Test force_refresh bypasses cache."""

        concept_data = {
            "conceptId": 201826,
            "conceptName": "Type 2 diabetes mellitus",
            "vocabularyId": "SNOMED",
            "conceptCode": "44054006",
            "conceptClassId": "Clinical Finding",
            "standardConcept": "S",
            "domainId": "Condition",
            "validStartDate": "1970-01-01",
            "validEndDate": "2099-12-31",
            "invalidReason": None,
        }

        call_count = 0

        def mock_response(request):
            nonlocal call_count
            call_count += 1
            # Modify response slightly to track freshness
            data = concept_data.copy()
            data["conceptName"] = f"Type 2 diabetes mellitus (call {call_count})"
            return httpx.Response(200, json=data)

        respx.get(f"{self.base_url}/vocabulary/concept/201826").mock(side_effect=mock_response)

        # First call
        concept1 = self.client.vocabulary.get_concept(201826)
        assert call_count == 1
        assert "call 1" in concept1.conceptName

        # Second call with force_refresh
        concept2 = self.client.vocabulary.get_concept(201826, force_refresh=True)
        assert call_count == 2  # Additional API call
        assert "call 2" in concept2.conceptName

        # Third normal call - should still use original cache (not the force_refresh result)
        concept3 = self.client.vocabulary.get_concept(201826)
        assert call_count == 2  # No additional call
        assert "call 1" in concept3.conceptName  # Original cached result

    @respx.mock
    def test_vocabulary_search_caching(self):
        """Test that vocabulary.search properly caches results."""

        search_results = [
            {
                "conceptId": 201826,
                "conceptName": "Type 2 diabetes mellitus",
                "vocabularyId": "SNOMED",
                "conceptCode": "44054006",
                "conceptClassId": "Clinical Finding",
                "standardConcept": "S",
                "domainId": "Condition",
                "validStartDate": "1970-01-01",
                "validEndDate": "2099-12-31",
                "invalidReason": None,
            }
        ]

        call_count = 0

        def mock_search_response(request):
            nonlocal call_count
            call_count += 1
            return httpx.Response(200, json=search_results)

        respx.get(f"{self.base_url}/vocabulary/search").mock(side_effect=mock_search_response)

        # First search
        results1 = self.client.vocabulary.search("diabetes")
        assert call_count == 1
        assert len(results1) == 1

        # Same search - should use cache
        results2 = self.client.vocabulary.search("diabetes")
        assert call_count == 1  # No additional API call (should use cache)
        assert len(results2) == 1

        # Different search parameters - should not use cache
        self.client.vocabulary.search("diabetes", domain_id="Condition")
        assert call_count == 2  # Additional API call

        # Verify cache contents
        contents = cache_contents()
        assert len(contents["entries"]) == 2

        cache_keys = [entry["key"] for entry in contents["entries"]]
        assert 'VocabularyService.search("diabetes", page=1, page_size=20)' in cache_keys
        assert 'VocabularyService.search("diabetes", domain_id="Condition", page=1, page_size=20)' in cache_keys

    @respx.mock
    def test_vocabulary_domains_caching(self):
        """Test that vocabulary.domains properly caches results."""

        domains_data = [
            {"domainId": "Condition", "domainName": "Condition"},
            {"domainId": "Drug", "domainName": "Drug"},
            {"domainId": "Procedure", "domainName": "Procedure"},
        ]

        call_count = 0

        def mock_domains_response(request):
            nonlocal call_count
            call_count += 1
            return httpx.Response(200, json=domains_data)

        respx.get(f"{self.base_url}/vocabulary/domains").mock(side_effect=mock_domains_response)

        # First call
        domains1 = self.client.vocabulary.domains()
        assert call_count == 1
        assert len(domains1) == 3

        # Second call - should use cache
        domains2 = self.client.vocabulary.domains()
        assert call_count == 1  # No additional API call
        assert len(domains2) == 3

        # Verify cache contents
        contents = cache_contents()
        assert len(contents["entries"]) == 1
        assert contents["entries"][0]["key"] == "VocabularyService.list_domains()"
        assert "list (3 items)" in contents["entries"][0]["data_type"]

    @respx.mock
    def test_multiple_services_cache_isolation(self):
        """Test that different services maintain separate cache entries."""

        # Mock vocabulary response
        concept_data = {
            "conceptId": 123,
            "conceptName": "Test Concept",
            "vocabularyId": "SNOMED",
            "conceptCode": "123456",
            "conceptClassId": "Clinical Finding",
            "standardConcept": "S",
            "domainId": "Condition",
            "validStartDate": "1970-01-01",
            "validEndDate": "2099-12-31",
            "invalidReason": None,
        }

        # Mock concept sets response
        concept_set_data = {"id": 123, "name": "Test Concept Set", "expression": {"items": []}}

        respx.get(f"{self.base_url}/vocabulary/concept/123").mock(return_value=httpx.Response(200, json=concept_data))
        respx.get(f"{self.base_url}/conceptset/123").mock(return_value=httpx.Response(200, json=concept_set_data))

        # Call both services with same ID
        concept = self.client.vocabulary.get_concept(123)
        concept_set = self.client.concept_sets.get(123)

        assert concept.conceptId == 123
        assert concept_set.id == 123

        # Verify separate cache entries
        contents = cache_contents()
        assert len(contents["entries"]) == 2

        cache_keys = [entry["key"] for entry in contents["entries"]]
        assert "VocabularyService.get_concept(123)" in cache_keys
        assert "ConceptSetService.get(123)" in cache_keys

    def test_cache_disabled_globally(self):
        """Test behavior when caching is disabled globally."""

        with patch("ohdsi_webapi.cache.CACHE_ENABLED", False):
            # Even with cache disabled, functions should work
            stats = cache_stats()
            contents = cache_contents()

            assert "size" in stats
            assert "entries" in contents

            # Cache operations should still work (for testing purposes)
            clear_cache()

    @respx.mock
    def test_cache_ttl_expiration(self):
        """Test that cache entries expire based on TTL."""

        concept_data = {
            "conceptId": 201826,
            "conceptName": "Type 2 diabetes mellitus",
            "vocabularyId": "SNOMED",
            "conceptCode": "44054006",
            "conceptClassId": "Clinical Finding",
            "standardConcept": "S",
            "domainId": "Condition",
            "validStartDate": "1970-01-01",
            "validEndDate": "2099-12-31",
            "invalidReason": None,
        }

        call_count = 0

        def mock_response(request):
            nonlocal call_count
            call_count += 1
            return httpx.Response(200, json=concept_data)

        respx.get(f"{self.base_url}/vocabulary/concept/201826").mock(side_effect=mock_response)

        # Patch the TTL to be very short for testing
        with patch("ohdsi_webapi.services.vocabulary.cached_method") as mock_cached:
            # Configure the decorator to use very short TTL
            def short_ttl_decorator(ttl_seconds=None):
                from ohdsi_webapi.cache import cached_method

                return cached_method(ttl_seconds=0.1)  # 100ms TTL

            mock_cached.return_value = short_ttl_decorator()

            # This test would require modifying the actual service method
            # For now, we'll test the cache mechanism directly
            from ohdsi_webapi.cache import _global_cache

            _global_cache.set("test_key", "test_value", ttl_seconds=0.1)

            # Immediately should be available
            assert _global_cache.get("test_key") == "test_value"

            # After TTL expires
            time.sleep(0.15)
            assert _global_cache.get("test_key") is None


if __name__ == "__main__":
    pytest.main([__file__])
