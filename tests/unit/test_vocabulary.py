import httpx
import respx
from ohdsi_webapi import WebApiClient


@respx.mock
def test_get_concept():
    respx.get("http://test/WebAPI/vocabulary/concept/201826").mock(
        return_value=httpx.Response(200, json={"conceptId": 201826, "conceptName": "Metformin", "vocabularyId": "RxNorm"})
    )
    client = WebApiClient("http://test/WebAPI")
    try:
        c = client.vocab.get_concept(201826)
        assert c.concept_name == "Metformin"
    finally:
        client.close()
