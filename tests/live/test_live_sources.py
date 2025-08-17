import pytest


@pytest.mark.webapi_integration()
def test_live_sources_new_api(live_client):
    """Test the new source.sources() API."""
    sources = live_client.source.sources()
    assert isinstance(sources, list)
    if not sources:
        pytest.skip("No sources returned from live server")
    assert all(hasattr(s, "source_key") for s in sources)


@pytest.mark.webapi_integration()
def test_live_sources_list_backward_compatibility(live_client):
    """Test backward compatibility of source.list()."""
    sources = live_client.source.list()
    assert isinstance(sources, list)
    if not sources:
        pytest.skip("No sources returned from live server")
    assert all(hasattr(s, "source_key") for s in sources)


@pytest.mark.webapi_integration()
def test_live_client_sources_shortcut(live_client):
    """Test the client.sources() shortcut."""
    sources = live_client.sources()
    assert isinstance(sources, list)
    if not sources:
        pytest.skip("No sources returned from live server")
    assert all(hasattr(s, "source_key") for s in sources)
