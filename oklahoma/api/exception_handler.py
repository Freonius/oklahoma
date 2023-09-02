from typing import Callable
from traceback import format_exception
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from starlette.middleware.exceptions import ExceptionMiddleware
from ..log import logger


async def _handle_exception(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(f"Got exception for url {request.url}")
    logger.exception(exc)
    return JSONResponse(
        content={
            "message": "Internal Server Error",
            "reason": "\n".join(format_exception(exc))
            if __debug__
            else "Internal Server Error",
        },
        status_code=500,
    )


class GenericExceptionMiddleware(ExceptionMiddleware):
    def _lookup_exception_handler(self, exc: Exception) -> Callable | None:
        if isinstance(exc, HTTPException):
            return super()._lookup_exception_handler(exc)
        else:
            return self.__exception_handler

    # @classmethod
    # async def __http_exception_handler(
    #     cls, request: Request, ex: HTTPException,
    # ):
    #     return _handle_exception(request, ex)

    @classmethod
    async def __exception_handler(
        cls,
        request: Request,
        ex: Exception,
    ) -> JSONResponse:
        return await _handle_exception(request, ex)


def set_exception_handler(app: FastAPI) -> None:
    if app.debug is True:
        app.add_middleware(
            GenericExceptionMiddleware,
            debug=app.debug,
        )
    app.exception_handler(Exception)(_handle_exception)
