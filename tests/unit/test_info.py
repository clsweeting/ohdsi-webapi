import httpx
import respx
from ohdsi_webapi import WebApiClient


@respx.mock
def test_info_version():
    route = respx.get("http://test/WebAPI/info").mock(return_value=httpx.Response(200, json={"version": "2.13.0"}))
    client = WebApiClient("http://test/WebAPI")
    try:
        ver = client.info_service.version()
        assert route.called
        assert ver == "2.13.0"
    finally:
        client.close()


@respx.mock
def test_info_service_get():
    """Test the service get() method."""
    route = respx.get("http://test/WebAPI/info").mock(return_value=httpx.Response(200, json={"version": "2.13.0", "buildNumber": "123"}))
    client = WebApiClient("http://test/WebAPI")
    try:
        info = client.info_service.get()
        assert route.called
        assert info.version == "2.13.0"
    finally:
        client.close()


@respx.mock
def test_info_shortcut():
    """Test the new client.info() shortcut method."""
    route = respx.get("http://test/WebAPI/info").mock(return_value=httpx.Response(200, json={"version": "2.13.0", "buildNumber": "123"}))
    client = WebApiClient("http://test/WebAPI")
    try:
        info = client.info()
        assert route.called
        assert info.version == "2.13.0"
    finally:
        client.close()


@respx.mock
def test_info_methods_equivalent():
    """Test that both info methods return equivalent data."""
    respx.get("http://test/WebAPI/info").mock(return_value=httpx.Response(200, json={"version": "2.13.0", "buildNumber": "123"}))
    client = WebApiClient("http://test/WebAPI")
    try:
        info1 = client.info_service.get()
        info2 = client.info()
        assert info1.version == info2.version
        assert type(info1) == type(info2)
    finally:
        client.close()
