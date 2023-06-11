from fastapi.exceptions import HTTPException


class NotFound(HTTPException):
    """Not found error"""

    def __init__(
        self,
        headers: dict[str, object] | None = None,
    ) -> None:
        """404: Not found

        Args:
            headers (dict[str, object] | None, optional): headers. Defaults to None.
        """
        super().__init__(404, "Not found", headers)
