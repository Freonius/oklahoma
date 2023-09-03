from starlette.testclient import TestClient
from oklahoma.fixtures import APIFixture


def test_pytest_fixture_is_loaded(client):
    assert isinstance(client, TestClient)
    resp = client.get("/healthcheck")
    assert resp.status_code == 200


class TestApiV1First(APIFixture):
    def test_get_base(self) -> None:
        with self.get() as resp:
            resp.assert_is_ok()
            resp.assert_milliseconds(200)

    def test_get_other(self) -> None:
        with self.get("/other") as resp:
            resp.assert_is_ok()
            resp.assert_milliseconds(200)
