from fastapi import FastAPI
from uvicorn import run as uvrun
from ..environment import environ
from .routes_loader import RoutesLoader


def get_app() -> FastAPI:
    """Get the FastAPI app (except for testing purposes, \
        you don't really need to use this, it\
        should be transparent if you launch it with the module)"""
    environ.__reload__()
    app: FastAPI = FastAPI(
        debug=not environ.profile.app.prod,
        title=environ.profile.app.name,
        version=environ.profile.app.version,
        openapi_url="/openapi.json" if environ.profile.app.openapi.include else None,
        docs_url="/docs" if environ.profile.app.openapi.include else None,
    )
    _rl: RoutesLoader = RoutesLoader(
        environ.module,
        environ.cwd,
    )
    # Load all the routes
    _rl.load_routes()
    for _route in _rl.routes:
        app.include_router(_route)
    # Finished loading routes
    return app


def run() -> None:
    """Run the app"""
    app: FastAPI = get_app()
    uvrun(
        app,
        host="0.0.0.0",
        port=environ.profile.app.port,
    )
