import respx
import httpx
from ohdsi_webapi import WebApiClient

@respx.mock
def test_concept_set_crud():
    # Create
    respx.post("http://test/WebAPI/conceptset/").mock(return_value=httpx.Response(200, json={"id": 10, "name": "Test CS"}))
    # Get
    respx.get("http://test/WebAPI/conceptset/10").mock(return_value=httpx.Response(200, json={"id": 10, "name": "Test CS"}))
    client = WebApiClient("http://test/WebAPI")
    try:
        created = client.concept_sets.create("Test CS")
        fetched = client.concept_sets.get(created.id)  # type: ignore[arg-type]
        assert fetched.id == 10
        assert fetched.name == "Test CS"
    finally:
        client.close()
