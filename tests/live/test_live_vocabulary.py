import pytest

@pytest.mark.webapi_integration
def test_live_get_concept(live_client):
    """Test getting a known concept."""
    concept = live_client.vocabulary.get_concept(201826)  # Type 2 diabetes mellitus
    assert concept.conceptName == "Type 2 diabetes mellitus"
    assert concept.conceptId == 201826
    assert concept.domainId == "Condition"

@pytest.mark.webapi_integration  
def test_live_domains(live_client):
    """Test getting vocabulary domains."""
    domains = live_client.vocabulary.domains()
    assert len(domains) > 0
    # Check that domains have the expected structure
    domain_ids = [d.get('domainId') if isinstance(d, dict) else d.domainId for d in domains]
    assert 'Condition' in domain_ids
    assert 'Drug' in domain_ids

@pytest.mark.webapi_integration
def test_live_search(live_client):
    """Test searching for concepts."""
    # Test basic search
    results = live_client.vocabulary.search("diabetes", page_size=5)
    assert len(results) > 0
    assert any("diabetes" in c.conceptName.lower() for c in results)
    
    # Test search with domain filter
    condition_results = live_client.vocabulary.search("diabetes", domain_id="Condition", page_size=3)
    assert len(condition_results) > 0
    # All results should be conditions
    assert all(c.domainId == "Condition" for c in condition_results)
