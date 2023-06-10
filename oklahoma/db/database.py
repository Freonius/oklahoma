from os import environ
from typing import Type, Annotated
from types import TracebackType
from contextlib import suppress
from fastapi import Depends
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session


class Database:
    _engine: Engine
    _sessionmaker: sessionmaker[Session]
    _session: Session | None

    def __init__(self) -> None:
        self._engine = create_engine(
            environ["DB_URI"],
            echo=False,
        )
        self._sessionmaker = sessionmaker(bind=self._engine)
        self._session = None

    def __enter__(self) -> "Session":
        self._session = self._sessionmaker()
        return self._session

    def __exit__(
        self,
        exctype: Type[BaseException] | None,
        excinst: BaseException | None,
        exctb: TracebackType | None,
    ):
        if self._session is not None:
            self._session.close()

    @property
    def session(self) -> "Session":
        if self._session is not None:
            return self._session
        self._session = self._sessionmaker()
        return self._session

    def __del__(self) -> None:
        with suppress(Exception):
            self._engine.dispose()


def _get_db():
    with Database() as session:
        yield session


CurrentSession = Annotated[Session, Depends(_get_db)]
