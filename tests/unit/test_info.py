import respx
import httpx
from ohdsi_webapi import WebApiClient

@respx.mock
def test_info_version():
    route = respx.get("http://test/WebAPI/info").mock(return_value=httpx.Response(200, json={"version": "2.13.0"}))
    client = WebApiClient("http://test/WebAPI")
    try:
        ver = client.info.version()
        assert route.called
        assert ver == "2.13.0"
    finally:
        client.close()
