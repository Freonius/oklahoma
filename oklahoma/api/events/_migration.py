from threading import Thread
from typing import Callable
from fastapi import FastAPI
from ...log import logger
from ...utils import accepts_kwargs


def migration(
    app: FastAPI,
    before_migration: Callable[..., None],
    after_migration: Callable[..., None],
) -> None:
    def _background_task() -> None:
        logger.info("Running event before_migration")
        if accepts_kwargs(before_migration) is True:
            before_migration(app=app)
        else:
            before_migration()
        logger.info("Running event before_migration")
        logger.info("Running migration")
        # TODO: run migration
        logger.info("Migration finished")
        logger.info("Running event after_migration")
        if accepts_kwargs(after_migration) is True:
            after_migration(app=app)
        else:
            after_migration()
        logger.info("After migration finished")

    _th: Thread = Thread(target=_background_task)
    _th.start()
