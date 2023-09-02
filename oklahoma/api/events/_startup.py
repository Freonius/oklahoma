from fastapi import FastAPI
from ...log import logger


def startup(app: FastAPI) -> None:
    logger.info("Startup")
