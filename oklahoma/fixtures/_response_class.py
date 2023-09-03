try:
    from httpx import Response

    class TestResponse(Response):
        """
        A custom response class for testing purposes.

        This class extends the `Response` class from the `httpx` \
        library and adds additional assertion methods for \
        testing API responses. It provides methods to check \
        if the response status code is within a certain range, \
        if the response elapsed time is within a certain threshold, \
        and if the JSON representation of the response is a list \
        or contains only dictionaries.

        """

        def assert_is_ok(self) -> None:
            """
            Asserts that the status code of the response is \
            within the range of 200 to 399.
            """
            assert self.status_code >= 200 and self.status_code < 400

        def assert_milliseconds(self, milliseconds: int = 200) -> None:
            """
            Check if the elapsed time in milliseconds is less \
            than or equal to the given number of milliseconds.

            Parameters:
                milliseconds (int): The maximum number of milliseconds \
                     the elapsed time can be.

            Returns:
                None
            """
            assert self.elapsed.microseconds <= milliseconds * 1000

        def assert_status_code(self, status_code: int = 200) -> None:
            """
            Asserts that the status code of the response \
            matches the expected status code.

            Parameters:
                status_code (int): The expected status \
                    code (default is 200).

            Returns:
                None
            """
            assert self.status_code == status_code

        def assert_is_dict(self) -> None:
            """
            Asserts that the JSON representation of the \
            object is a dictionary.
            """
            assert isinstance(self.json(), dict)

        def assert_is_list(
            self,
            min_length: int | None = None,
            max_length: int | None = None,
        ) -> None:
            """
            Assert that the JSON response is a list.
            If a minimum length is provided, assert that the \
                list is at least that long.
            If a maximum length is provided, assert that the \
                list is at most that long.

            Parameters:
                min_length (int | None): The minimum length of \
                    the list (optional).
                max_length (int | None): The maximum length of \
                    the list (optional).

            Returns:
                None
            """
            assert isinstance(self.json(), list)
            if min_length is not None:
                assert len(self.json()) >= min_length
            if max_length is not None:
                assert len(self.json()) <= max_length

        def assert_all_items_are_dicts(self) -> None:
            """
            Check if all items in the list are dictionaries.

            This function asserts that all items in the list \
            are dictionaries. It first checks if the list itself \
            is valid by calling the `assert_is_list()` function. \
            Then, it uses the `all()` function with a generator \
            expression to iterate over each item in the list and \
            check if it is an instance of the `dict` class. If any \
            item in the list is not a dictionary, the assertion \
            will fail.

            Returns:
                None
            """
            self.assert_is_list()
            assert all(isinstance(x, dict) for x in self.json())

        def __enter__(self) -> "TestResponse":
            return self

        def __exit__(self, *args: object, **kwargs: object) -> None:
            self.close()

except ImportError:
    pass
