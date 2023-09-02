from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from ..environment import Env


def create_custom_openapi_definition(app: FastAPI, env: Env) -> None:
    def custom_openapi() -> dict[str, object]:
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=env.profile.app.name,
            description="",
            version=env.profile.app.version,
            openapi_version="3.0.1",
            routes=app.routes,
        )
        _servers = env.profile.app.openapi.servers
        if len(_servers) > 0:
            openapi_schema["servers"] = [
                {"url": _servers[key], "description": key} for key in _servers
            ]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore
