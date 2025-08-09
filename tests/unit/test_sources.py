import respx
import httpx
from ohdsi_webapi import WebApiClient

@respx.mock
def test_list_sources():
    respx.get("http://test/WebAPI/source/sources").mock(return_value=httpx.Response(200, json=[
        {"sourceId": 1, "sourceName": "CDM", "sourceKey": "CDM", "sourceDialect": "postgresql", "daimons": []}
    ]))
    client = WebApiClient("http://test/WebAPI")
    try:
        sources = client.sources.list()
        assert len(sources) == 1
        assert sources[0].sourceKey == "CDM"
    finally:
        client.close()
