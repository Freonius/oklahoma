from os.path import isdir, sep
from os import makedirs
from json import dump
from fastapi import FastAPI, Response
from uvicorn import run as uvrun
from ..environment import environ
from ..log import logger
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
    logger.info("Loading routes")
    _rl.load_routes()
    for _route in _rl.routes:
        app.include_router(_route)
    logger.info("Routes loaded")
    # Finished loading routes

    @app.get(
        "/healthcheck",
        status_code=200,
        tags=["healthcheck"],
        summary="An endpoint to invoke for the healthcheck",
    )
    async def healtcheck() -> Response:
        """Perform an healthcheck and returns an\
        empty response.
        """
        return Response("", 200, media_type="text/plain")

    return app


def run(action: str | None = None) -> None:
    """Run the app"""
    app: FastAPI = get_app()
    logger.info(r"   ____  _    _       _                           _ ")
    logger.info(r"  / __ \| |  | |     | |                         | |")
    logger.info(r" | |  | | | _| | __ _| |__   ___  _ __ ___   __ _| |")
    logger.info(r" | |  | | |/ / |/ _` | '_ \ / _ \| '_ ` _ \ / _` | |")
    logger.info(r" | |__| |   <| | (_| | | | | (_) | | | | | | (_| |_|")
    logger.info(r"  \____/|_|\_\_|\__,_|_| |_|\___/|_| |_| |_|\__,_(_)")
    logger.info(r"                                                    ")
    logger.info(r" ================================================== ")
    logger.info("")
    logger.info("Saving openapi specifications to ./specs")
    _specs: str = "." + sep + "specs" + sep
    if not isdir(_specs):
        makedirs(_specs)
    with open(_specs + "openapi.json", "w", encoding="utf-8") as handle:
        dump(app.openapi(), handle)
    del _specs
    if action is not None and action.lower() == "openapi":
        return
    logger.info("Openapi specifications saved to ./specs")
    logger.info(f"Running application on port {environ.profile.app.port}")
    uvrun(
        app,
        host="0.0.0.0",
        port=environ.profile.app.port,
    )
