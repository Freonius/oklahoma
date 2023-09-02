from fastapi import FastAPI
from ...log import logger


def shutdown(app: FastAPI) -> None:
    logger.info("Shutdown")
