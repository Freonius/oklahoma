from doctest import debug
from os.path import isdir, sep
from os import makedirs
from json import dump
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as uvrun
from ..environment import environ
from ..log import logger
from ..utils import load_functions, accepts_kwargs
from .routes_loader import RoutesLoader
from .events import startup, shutdown, migration
from .exception_handler import set_exception_handler
from .openapi_definition import create_custom_openapi_definition


def get_app() -> FastAPI:
    """Get the FastAPI app (except for testing purposes, \
        you don't really need to use this, it\
        should be transparent if you launch it with the module)"""
    environ.__reload__()

    _events = load_functions(
        "before_startup",
        "after_startup",
        "before_migration",
        "after_migration",
        "on_shutdown",
        cwd=environ.cwd,
        folder_name=environ.module,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        try:
            logger.info("Running event before_startup")
            if accepts_kwargs(_events["before_startup"]) is True:
                _events["before_startup"](app=app)
            else:
                _events["before_startup"]()
            logger.info("Before startup finished")
            startup(app=app)
            logger.info("Running event after_startup")
            # TODO: Wait for db and services startup
            if accepts_kwargs(_events["after_startup"]) is True:
                _events["after_startup"](app=app)
            else:
                _events["after_startup"]()
            logger.info("After startup finished")

            if environ.profile.database.upgrade_at_start is True:
                migration(
                    app=app,
                    before_migration=_events["before_migration"],
                    after_migration=_events["after_migration"],
                )
            yield
        finally:
            if accepts_kwargs(_events["on_shutdown"]) is True:
                _events["on_shutdown"](app=app)
            else:
                _events["on_shutdown"]()
            shutdown(app=app)
            logger.info("Shut down complete")

    app: FastAPI = FastAPI(
        debug=not environ.profile.app.prod,
        title=environ.profile.app.name,
        version=environ.profile.app.version,
        openapi_url="/openapi.json" if environ.profile.app.openapi.include else None,
        docs_url="/docs" if environ.profile.app.openapi.include else None,
        lifespan=lifespan,
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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=environ.profile.app.openapi.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    set_exception_handler(app)
    create_custom_openapi_definition(app, environ)
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
