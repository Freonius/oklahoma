from typing import Any, Dict
from fastapi.exceptions import HTTPException


class NotFound(HTTPException):
    def __init__(self, headers: Dict[str, Any] | None = None) -> None:
        super().__init__(404, "Not found", headers)
