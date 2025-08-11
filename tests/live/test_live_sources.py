import pytest


@pytest.mark.webapi_integration()
def test_live_sources_list(live_client):
    sources = live_client.sources()
    assert isinstance(sources, list)
    if not sources:
        pytest.skip("No sources returned from live server")
    assert all(hasattr(s, "source_key") for s in sources)
