import httpx
import respx
from ohdsi_webapi import WebApiClient


@respx.mock
def test_sources():
    """Test the new sources() method."""
    respx.get("http://test/WebAPI/source/sources").mock(
        return_value=httpx.Response(
            200, json=[{"sourceId": 1, "sourceName": "CDM", "sourceKey": "CDM", "sourceDialect": "postgresql", "daimons": []}]
        )
    )
    client = WebApiClient("http://test/WebAPI")
    try:
        sources = client.source.sources()
        assert len(sources) == 1
        assert sources[0].source_key == "CDM"
    finally:
        client.close()


@respx.mock
def test_list_sources_backward_compatibility():
    """Test backward compatibility of the old list() method."""
    respx.get("http://test/WebAPI/source/sources").mock(
        return_value=httpx.Response(
            200, json=[{"sourceId": 1, "sourceName": "CDM", "sourceKey": "CDM", "sourceDialect": "postgresql", "daimons": []}]
        )
    )
    client = WebApiClient("http://test/WebAPI")
    try:
        # Test old service.list() method
        sources = client.source.list()
        assert len(sources) == 1
        assert sources[0].source_key == "CDM"
    finally:
        client.close()


@respx.mock
def test_client_sources_shortcut():
    """Test the client.sources() shortcut method."""
    respx.get("http://test/WebAPI/source/sources").mock(
        return_value=httpx.Response(
            200, json=[{"sourceId": 1, "sourceName": "CDM", "sourceKey": "CDM", "sourceDialect": "postgresql", "daimons": []}]
        )
    )
    client = WebApiClient("http://test/WebAPI")
    try:
        # Test client.sources() shortcut
        sources = client.sources()
        assert len(sources) == 1
        assert sources[0].source_key == "CDM"
    finally:
        client.close()
