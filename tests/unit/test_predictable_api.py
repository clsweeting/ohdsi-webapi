"""Tests for predictable API naming patterns that mirror REST endpoints."""

import pytest
from ohdsi_webapi import WebApiClient


class TestPredictableAPI:
    """Test the predictable API naming convention."""

    @pytest.fixture()
    def client(self):
        """Create a test client."""
        return WebApiClient("https://test.example.com")

    def test_conceptset_callable_interface(self, client):
        """Test that conceptset is callable for REST-style access."""
        # Should be callable
        assert callable(client.conceptset)

        # Should delegate to underlying service methods
        assert hasattr(client.conceptset, "list")
        assert hasattr(client.conceptset, "get")
        assert hasattr(client.conceptset, "create")
        assert hasattr(client.conceptset, "update")
        assert hasattr(client.conceptset, "delete")

    def test_cohortdefinition_callable_interface(self, client):
        """Test that cohortdefinition is callable for REST-style access."""
        # Should be callable
        assert callable(client.cohortdefinition)

        # Should delegate to underlying service methods
        assert hasattr(client.cohortdefinition, "list")
        assert hasattr(client.cohortdefinition, "get")
        assert hasattr(client.cohortdefinition, "create")
        assert hasattr(client.cohortdefinition, "update")
        assert hasattr(client.cohortdefinition, "delete")

    def test_conceptset_subresource_methods(self, client):
        """Test that conceptset sub-resource methods are dynamically available."""
        # These should be available via __getattr__
        assert hasattr(client, "conceptset_expression")
        assert hasattr(client, "conceptset_items")
        assert hasattr(client, "conceptset_export")
        assert hasattr(client, "conceptset_generationinfo")

        # Should be callable
        assert callable(client.conceptset_expression)
        assert callable(client.conceptset_items)
        assert callable(client.conceptset_export)
        assert callable(client.conceptset_generationinfo)

    def test_cohortdefinition_subresource_methods(self, client):
        """Test that cohortdefinition sub-resource methods are dynamically available."""
        # These should be available via __getattr__
        assert hasattr(client, "cohortdefinition_generate")
        assert hasattr(client, "cohortdefinition_info")
        assert hasattr(client, "cohortdefinition_inclusionrules")

        # Should be callable
        assert callable(client.cohortdefinition_generate)
        assert callable(client.cohortdefinition_info)
        assert callable(client.cohortdefinition_inclusionrules)

    def test_info_callable_interface(self, client):
        """Test that info is callable for REST-style access."""
        # Should be callable
        assert callable(client.info)

        # Should delegate to underlying service methods
        assert hasattr(client.info, "get")
        assert hasattr(client.info, "version")

    def test_source_sources_predictable_method(self, client):
        """Test that source_sources method is available."""
        # Should be available via __getattr__
        assert hasattr(client, "source_sources")

        # Should be callable
        assert callable(client.source_sources)

    def test_job_predictable_method(self, client):
        """Test that job method is available."""
        # Should be available via __getattr__
        assert hasattr(client, "job")

        # Should be callable
        assert callable(client.job)

    def test_backwards_compatibility(self, client):
        """Test that existing service-based API still works."""
        # Original service attributes should exist
        assert hasattr(client, "concept_sets")
        assert hasattr(client, "cohorts")
        assert hasattr(client, "vocabulary")
        assert hasattr(client, "vocab")

        # Original methods should be callable
        assert callable(client.concept_sets.list)
        assert callable(client.concept_sets.get)
        assert callable(client.cohorts.list)
        assert callable(client.cohorts.get)
        assert callable(client.vocabulary.search)

    def test_vocabulary_predictable_methods(self, client):
        """Test that vocabulary service has predictable methods."""
        # Vocabulary should support both full name and alias
        assert hasattr(client, "vocabulary")
        assert hasattr(client, "vocab")
        assert client.vocab is client.vocabulary

        # Should have predictable method names
        assert hasattr(client.vocabulary, "concept_descendants")
        assert hasattr(client.vocabulary, "concept_related")
        assert hasattr(client.vocabulary, "concepts")
        assert hasattr(client.vocabulary, "vocabularies")
        assert hasattr(client.vocabulary, "domains")

    def test_unknown_subresource_raises_error(self, client):
        """Test that unknown sub-resource methods raise appropriate errors."""
        with pytest.raises(AttributeError, match="Unknown conceptset sub-resource"):
            _ = client.conceptset_unknown_method

        with pytest.raises(AttributeError, match="Unknown cohortdefinition sub-resource"):
            _ = client.cohortdefinition_unknown_method

    def test_unknown_attribute_raises_error(self, client):
        """Test that completely unknown attributes raise AttributeError."""
        with pytest.raises(AttributeError, match="object has no attribute"):
            _ = client.completely_unknown_attribute

    def test_predictable_wrapper_delegation(self, client):
        """Test that PredictableServiceWrapper properly delegates attributes."""
        # Wrapper should delegate all service methods
        wrapper = client.conceptset

        # Check that delegation works for common methods
        assert hasattr(wrapper, "list")
        assert hasattr(wrapper, "get")
        assert hasattr(wrapper, "create")

        # The delegated methods should be callable and equivalent
        assert callable(wrapper.list)
        assert callable(wrapper.get)
        assert callable(wrapper.create)

        # Wrapper should be callable itself
        assert callable(wrapper)
