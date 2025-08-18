"""Tests for explicit REST-style convenience methods and service interfaces."""

import pytest
from ohdsi_webapi import WebApiClient


class TestExplicitAPI:
    """Test the explicit API methods and service interfaces."""

    @pytest.fixture()
    def client(self):
        """Create a test client."""
        return WebApiClient("https://test.example.com")

    def test_core_service_interfaces(self, client):
        """Test that core service objects are available."""
        # Core services should exist
        assert hasattr(client, "concept_sets")
        assert hasattr(client, "cohortdefs")
        assert hasattr(client, "vocabulary")
        assert hasattr(client, "vocab")
        assert hasattr(client, "info")
        assert hasattr(client, "sources")
        assert hasattr(client, "jobs")

        # Vocabulary alias should work
        assert client.vocab is client.vocabulary

        # Services should have their standard methods
        assert hasattr(client.concept_sets, "list")
        assert hasattr(client.concept_sets, "get")
        assert hasattr(client.concept_sets, "create")
        assert hasattr(client.concept_sets, "expression")
        assert hasattr(client.concept_sets, "resolve")

        assert hasattr(client.cohortdefs, "list")
        assert hasattr(client.cohortdefs, "get")
        assert hasattr(client.cohortdefs, "generate")
        assert hasattr(client.cohortdefs, "generation_status")

    def test_conceptset_convenience_methods(self, client):
        """Test that conceptset convenience methods are explicitly available."""
        # These should be explicit attributes (not dynamic)
        assert hasattr(client, "conceptset_expression")
        assert hasattr(client, "conceptset_items")
        assert hasattr(client, "conceptset_export")
        assert hasattr(client, "conceptset_generationinfo")

        # Should be callable
        assert callable(client.conceptset_expression)
        assert callable(client.conceptset_items)
        assert callable(client.conceptset_export)
        assert callable(client.conceptset_generationinfo)

        # Should be the same as the service methods
        assert client.conceptset_expression == client.concept_sets.expression
        assert client.conceptset_items == client.concept_sets.resolve
        assert client.conceptset_export == client.concept_sets.export
        assert client.conceptset_generationinfo == client.concept_sets.generation_info

    def test_cohortdefinition_convenience_methods(self, client):
        """Test that cohortdefinition convenience methods are explicitly available."""
        # These should be explicit attributes (not dynamic)
        assert hasattr(client, "cohortdefinition_generate")
        assert hasattr(client, "cohortdefinition_info")
        assert hasattr(client, "cohortdefinition_inclusionrules")

        # Should be callable
        assert callable(client.cohortdefinition_generate)
        assert callable(client.cohortdefinition_info)
        assert callable(client.cohortdefinition_inclusionrules)

        # Should be the same as the service methods
        assert client.cohortdefinition_generate == client.cohortdefs.generate
        assert client.cohortdefinition_info == client.cohortdefs.generation_status
        assert client.cohortdefinition_inclusionrules == client.cohortdefs.inclusion_rules

    def test_job_convenience_methods(self, client):
        """Test that job convenience methods are available."""
        # Should have explicit job status method
        assert hasattr(client, "job_status")
        assert callable(client.job_status)
        assert client.job_status == client.jobs.status

    def test_service_method_compatibility(self, client):
        """Test that service-based API still works as primary interface."""
        # Original service methods should be callable
        assert callable(client.concept_sets.list)
        assert callable(client.concept_sets.get)
        assert callable(client.cohortdefs.list)
        assert callable(client.cohortdefs.get)
        assert callable(client.vocabulary.search)
        assert callable(client.info)  # info is now a shortcut method, not a service
        assert callable(client.source.sources)

    def test_vocabulary_methods(self, client):
        """Test that vocabulary service has expected methods."""
        # Should have standard vocabulary methods
        assert hasattr(client.vocabulary, "concept_descendants")
        assert hasattr(client.vocabulary, "concept_related")
        assert hasattr(client.vocabulary, "search")
        assert hasattr(client.vocabulary, "list_vocabularies")
        assert hasattr(client.vocabulary, "list_domains")

        # Methods should be callable
        assert callable(client.vocabulary.search)
        assert callable(client.vocabulary.concept_descendants)

    def test_unknown_attribute_raises_error(self, client):
        """Test that unknown attributes raise AttributeError."""
        with pytest.raises(AttributeError):
            _ = client.completely_unknown_attribute

        with pytest.raises(AttributeError):
            _ = client.unknown_convenience_method

    def test_no_dynamic_method_generation(self, client):
        """Test that we don't have dynamic method generation anymore."""
        # These should NOT exist (we removed the dynamic __getattr__ magic)
        assert not hasattr(client, "conceptset_unknown_method")
        assert not hasattr(client, "cohortdefinition_unknown_method")

        # Some specific convenience methods are still intentionally available
        assert callable(getattr(client, "conceptset", None))  # Explicit convenience method
        assert callable(getattr(client, "cohortdefinition", None))  # Explicit convenience method

    def test_cache_management_methods(self, client):
        """Test that cache management methods are available."""
        assert hasattr(client, "clear_cache")
        assert hasattr(client, "cache_stats")
        assert callable(client.clear_cache)
        assert callable(client.cache_stats)

    def test_context_manager_support(self, client):
        """Test that context manager protocol is supported."""
        assert hasattr(client, "__enter__")
        assert hasattr(client, "__exit__")
        assert hasattr(client, "close")

        # Should be usable as context manager
        with client:
            pass  # Should not raise
