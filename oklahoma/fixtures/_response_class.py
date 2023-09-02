try:
    from httpx import Response

    class TestResponse(Response):
        def assert_is_ok(self) -> None:
            assert self.status_code >= 200 and self.status_code < 400

        def assert_milliseconds(self, milliseconds: int = 200) -> None:
            assert self.elapsed.microseconds <= milliseconds * 1000

        def assert_status_code(self, status_code: int = 200) -> None:
            assert self.status_code == status_code

        def assert_is_dict(self) -> None:
            assert isinstance(self.json(), dict)

        def assert_is_list(
            self,
            min_length: int | None = None,
            max_length: int | None = None,
        ) -> None:
            assert isinstance(self.json(), list)
            if min_length is not None:
                assert len(self.json()) >= min_length
            if max_length is not None:
                assert len(self.json()) <= max_length

        def assert_all_items_are_dicts(self) -> None:
            self.assert_is_list()
            assert all(isinstance(x, dict) for x in self.json())

        def __enter__(self) -> "TestResponse":
            return self

        def __exit__(self, *args: object, **kwargs: object) -> None:
            self.close()

except ImportError:
    pass
