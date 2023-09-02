from typing import Generator


try:
    from pytest import fixture
    from starlette.testclient import TestClient
    from ..api import get_app

    def _get_client() -> TestClient:
        testclient: TestClient = TestClient(get_app())
        # TODO: Find if there's a function called "insert_test_data" in conftest.py
        return testclient

    @fixture(scope="session")
    def client() -> Generator[TestClient, None, None]:
        """Test client for the whole session"""
        yield _get_client()

except ImportError:
    pass
