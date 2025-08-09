import httpx
import respx
from ohdsi_webapi import WebApiClient


@respx.mock
def test_cohort_get():
    respx.get("http://test/WebAPI/cohortdefinition/5").mock(
        return_value=httpx.Response(
            200, json={"id": 5, "name": "Test Cohort", "expressionType": "SIMPLE_EXPRESSION", "expression": {"PrimaryCriteria": {}}}
        )
    )
    client = WebApiClient("http://test/WebAPI")
    try:
        coh = client.cohorts.get(5)
        assert coh.name == "Test Cohort"
    finally:
        client.close()
