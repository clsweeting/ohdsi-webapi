import pytest
from ohdsi_webapi.exceptions import NotFoundError


@pytest.mark.webapi_integration()
def test_live_concept_set_listing_and_resolve(live_client):
    """Test concept set operations."""
    sets = live_client.concept_sets.list()
    if not sets:
        pytest.skip("No concept sets returned from live server")

    first = sets[0]

    # Test getting the concept set
    cs = live_client.concept_sets.get(first.id)  # type: ignore[arg-type]
    assert cs.id == first.id

    # Test getting the expression
    expr = live_client.concept_sets.expression(first.id)  # type: ignore[arg-type]
    assert isinstance(expr, dict)

    # Test resolve - this may not work for all concept sets
    try:
        resolved = live_client.concept_sets.resolve(first.id)  # type: ignore[arg-type]
        assert isinstance(resolved, list)
    except NotFoundError:
        # Some concept sets may not have resolved concepts available
        # This is acceptable for the demo server
        pytest.skip(f"Concept set {first.id} does not have resolved concepts available")
