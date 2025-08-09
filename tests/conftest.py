import os
import pytest
from ohdsi_webapi import WebApiClient

LIVE_ENV = "INTEGRATION_WEBAPI"

@pytest.fixture(scope="session")
def live_client():
    base = os.getenv("OHDSI_WEBAPI_BASE_URL", "https://atlas-demo.ohdsi.org/WebAPI")
    if not os.getenv(LIVE_ENV):
        pytest.skip("Set INTEGRATION_WEBAPI=1 to run live WebAPI tests")
    client = WebApiClient(base)
    yield client
    client.close()

def pytest_collection_modifyitems(config, items):
    if os.getenv(LIVE_ENV):
        return
    skip_live = pytest.mark.skip(reason="Set INTEGRATION_WEBAPI=1 to run live tests")
    for item in items:
        # Mark any test under tests/live or with marker
        if "tests/live/" in str(item.fspath) or "webapi_integration" in item.keywords:
            item.add_marker(skip_live)
