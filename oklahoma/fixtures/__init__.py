from typing import Generator

try:
    from pytest import fixture
    from starlette.testclient import TestClient
    from ..api import get_app

    @fixture(scope="session")
    def client() -> Generator[TestClient, None, None]:
        """Test client for the whole session"""
        yield TestClient(get_app())

except ImportError:
    pass
