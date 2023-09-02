from oklahoma.fixtures import APIFixture


def test_pytest_is_running():
    assert True


class TestApiV1First(APIFixture):
    def test_get_base(self) -> None:
        with self.get() as resp:
            resp.assert_is_ok()
            resp.assert_milliseconds(200)

    def test_get_other(self) -> None:
        with self.get("/other") as resp:
            resp.assert_is_ok()
            resp.assert_milliseconds(200)
