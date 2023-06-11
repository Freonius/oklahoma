from re import sub
from datetime import datetime, date

from typing import Type
from typing_extensions import Self
from sqlalchemy import (
    Date,
    DateTime,
    Integer,
    Boolean,
    inspect,
)
from sqlalchemy.sql.functions import now
from sqlalchemy.sql.expression import asc, desc, ColumnElement
from sqlalchemy.orm import (
    Mapped,
    declared_attr,
    DeclarativeBase,
    mapped_column,
    Query,
    Session,
)

# pylint: disable=no-name-in-module
# from pydantic import BaseModel, create_model

# pylint: enable=no-name-in-module
from inflect import engine
from ..exceptions import SessionError
from .database import Database

inf_eng: engine = engine()


# declarative base class
class Base(DeclarativeBase):
    """Declarative base for all sqlalchemy models."""

    __exclude_fields__: tuple[str, ...] = tuple()

    # pylint: disable=no-self-argument
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return inf_eng.plural_noun(
            sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower(),
        )

    # pylint: enable=no-self-argument

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    created: Mapped[datetime] = mapped_column(server_default=now())
    updated: Mapped[datetime] = mapped_column(
        server_default=now(),
        server_onupdate=now(),  # type: ignore
    )

    def add(
        self,
        session: Session | None = None,
        *,
        commit: bool = True,
        flush: bool = True,
        refresh: bool = True,
    ) -> Session:
        """Add the current object to database.

        Args:
            session (Session | None, optional): The session.\
                It will create one if it's None. Defaults to None.
            commit (bool, optional): Autocommit. Defaults to True.
            flush (bool, optional): Auto-flush. Defaults to True.
            refresh (bool, optional): Auto refresh. Defaults to True.

        Returns:
            Session: The session used
        """
        if session is None and isinstance(
            (
                _tmp_session := getattr(
                    inspect(self),
                    "session",
                    None,
                ),
            ),
            Session,
        ):
            session = _tmp_session
        if session is None:
            session = Database().session
        session.add(self)
        if flush is True:
            session.flush()
        if commit is True:
            session.commit()
        if refresh is True:
            session.refresh(self)
        return session

    def update(
        self,
        session: Session | None = None,
        *,
        commit: bool = True,
        refresh: bool = True,
    ) -> Session:
        """Update the element.

        Args:
            session (Session | None, optional): The session to use.\
                Defaults to None.
            commit (bool, optional): Autocommit. Defaults to True.
            refresh (bool, optional): Autorefresh. Defaults to True.

        Returns:
            Session: The session used
        """
        if session is None and isinstance(
            (
                _tmp_session := getattr(
                    inspect(self),
                    "session",
                    None,
                ),
            ),
            Session,
        ):
            session = _tmp_session
        if session is None:
            session = Database().session
        session.flush()
        if commit is True:
            session.commit()
        if refresh is True:
            session.refresh(self)
        return session

    def delete(
        self,
        session: Session | None = None,
        *,
        commit: bool = True,
        flush: bool = True,
    ) -> Session:
        """Delete an element. If the "deleted" field is set, it will
        be used.

        Args:
            session (Session | None, optional): The current session.\
                  Defaults to None.
            commit (bool, optional): Autocommit. Defaults to True.
            flush (bool, optional): Autoflush. Defaults to True.

        Returns:
            Session: The session used
        """
        if session is None and isinstance(
            (
                _tmp_session := getattr(
                    inspect(self),
                    "session",
                    None,
                ),
            ),
            Session,
        ):
            session = _tmp_session
        if session is None:
            session = Database().session
        if any(getattr(c, "name", None) == "deleted" for c in self.__table__.columns):
            # pylint: disable=attribute-defined-outside-init
            self.deleted = self._get_deleted_value()
            # pylint: enable=attribute-defined-outside-init
        else:
            session.delete(self)
        if flush is True:
            session.flush()
        if commit is True:
            session.commit()
        return session

    @staticmethod
    def get_session() -> Session:
        """Create a session

        Returns:
            Session: The session
        """
        return Database().session

    @classmethod
    def get(
        cls,
        *args: ColumnElement[bool] | None | Session,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | list[str] | None = None,
        order: str | list[str] | None = None,
    ) -> list[Self]:
        """Find all elements that match a clause or all elements.

        Args:
            *args (ColumnElement[bool] | None | Session) list of conditions\
                (eg MyModel.id == 1), or Session, or None
            limit (int | None, optional): Limit. Defaults to None.
            offset (int | None, optional): Offset. Defaults to None.
            order_by (str | list[str] | None, optional): Order by column or list\
                of columns. Defaults to None.
            order (str | list[str] | None, optional): ASC or DESC. Defaults to None.

        Raises:
            SessionError: More than one session provided.

        Returns:
            list[Self]: Result
        """
        filters: list[ColumnElement[bool]] = [
            arg for arg in args if arg is not None and not isinstance(arg, Session)
        ]
        if (_del_filter := cls._delete_filter()) is not None:
            filters.append(_del_filter)
        database: Database = Database()
        session: Session | None = None
        sessions: list[Session] = [arg for arg in args if isinstance(arg, Session)]
        if len(sessions) > 1:
            raise SessionError("Found more than one session")
        if len(sessions) == 1:
            session = sessions[0]
        if session is None:
            session = database.session
        query: Query[Self] = session.query(cls)
        for _filter in filters:
            query = query.filter(_filter)
        # Order by
        if order_by is not None:
            if order is not None:
                if isinstance(order, str) and isinstance(order_by, str):
                    if order.upper().strip() == "ASC":
                        query = query.order_by(
                            asc(order_by),
                        )
                    elif order.upper().strip() == "DESC":
                        query = query.order_by(
                            desc(order_by),
                        )
                elif (
                    isinstance(order, list)
                    and isinstance(order_by, list)
                    and len(order) == len(order_by)
                ):
                    for order_el, order_by_el in zip(
                        order,
                        order_by,
                        strict=True,
                    ):
                        if order_el.upper().strip() == "ASC":
                            query = query.order_by(
                                asc(order_by_el),
                            )
                        elif order_el.upper().strip() == "DESC":
                            query = query.order_by(
                                desc(order_by_el),
                            )
            else:
                if isinstance(order_by, str):
                    query = query.order_by(order_by)
                else:
                    for order_by_el in order_by:
                        query = query.order_by(order_by_el)

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        return query.all()

    @classmethod
    def get_one(
        cls,
        *args: ColumnElement[bool] | None | Session,
    ) -> Self | None:
        """Find one or None
        Args:
            *args (ColumnElement[bool] | None | Session) list of conditions\
                (eg MyModel.id == 1), or Session, or None
            
        Raises:
            SessionError: More than one session provided.

        Returns:
            list[Self]: Result
        """
        filters: list[ColumnElement[bool]] = [
            arg for arg in args if arg is not None and not isinstance(arg, Session)
        ]
        if (_del_filter := cls._delete_filter()) is not None:
            filters.append(_del_filter)
        database: Database = Database()
        session: Session | None = None
        sessions: list[Session] = [arg for arg in args if isinstance(arg, Session)]
        if len(sessions) > 1:
            raise SessionError("Found more than one session")
        if len(sessions) == 1:
            session = sessions[0]
        if session is None:
            session = database.session
        query: Query[Self] = session.query(cls)
        for _filter in filters:
            query = query.filter(_filter)
        return query.one_or_none()

    def __to_dict(
        self,
        *origins: Type["Base"],
    ) -> dict[str, object]:
        """Transform to dict, checking for infinite recursion

        Returns:
            dict[str, object]: The dict object
        """
        out: dict[str, object] = {}
        for key in [getattr(c, "name", None) for c in self.__table__.columns]:
            if not isinstance(key, str):
                continue
            if (
                key in ("updated", "created", "deleted")
                or key in self.__exclude_fields__
            ):
                continue
            out[key] = getattr(self, key, None)
            if isinstance((_is_dt := out[key]), (date, datetime)):
                out[key] = _is_dt.isoformat()
            if (_tmp := out[key]) is not None and isinstance(_tmp, Base):
                if type(_tmp) in origins:
                    del out[key]
                    continue
                # pylint: disable=protected-access
                out[key] = _tmp.__to_dict(self.__class__, *origins)
                # pylint: enable=protected-access
        for key, _ in self.__mapper__.relationships.items():
            if key in self.__exclude_fields__:
                continue
            out[key] = getattr(self, key, None)
            if (_tmp := out[key]) is not None and isinstance(_tmp, Base):
                if type(_tmp) in origins:
                    del out[key]
                    continue
                # pylint: disable=protected-access
                out[key] = _tmp.__to_dict(self.__class__, *origins)
                # pylint: enable=protected-access
            elif (_tmp := out[key]) is not None and isinstance(_tmp, list):
                if any(type(x) in origins for x in _tmp):
                    del out[key]
                    continue
                # pylint: disable=protected-access
                out[key] = [
                    x.__to_dict(self.__class__, *origins)
                    for x in _tmp
                    if isinstance(x, Base)
                ]
                # pylint: enable=protected-access
        return out

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Transform the object to a dict, ready to be sent out.

        Returns:
            dict[str, object]: The dict object
        """
        return self.__to_dict()

    @classmethod
    def _delete_filter(cls) -> ColumnElement[bool] | None:
        for col in cls.__table__.columns:
            if getattr(col, "name", None) == "deleted":
                # pylint: disable=no-member
                if isinstance(col.type, DateTime):
                    return cls.deleted is None  # type: ignore
                if isinstance(col.type, Date):
                    return cls.deleted is None  # type: ignore
                if isinstance(col.type, Boolean):
                    return cls.deleted.in_([None, False])  # type: ignore
                if isinstance(col.type, Integer):
                    return cls.deleted.in_([None, 0])  # type: ignore
                # pylint: enable=no-member
        return None

    def _get_deleted_value(self) -> datetime | date | int | None | bool:
        for col in self.__table__.columns:
            if getattr(col, "name", None) == "deleted":
                if isinstance(col.type, DateTime):
                    return datetime.now()
                if isinstance(col.type, Date):
                    return date.today()
                if isinstance(col.type, Boolean):
                    return True
                if isinstance(col.type, Integer):
                    return 1
        return None

    # @classmethod
    # def get_out_model(cls) -> Type[BaseModel]:
    #     _def: dict[str, object] = {}
    #     for col in cls.__table__.columns:
    #         _name = getattr(col, "name", None)
    #         if (
    #             not isinstance(_name, str)
    #             or _name in ("updated", "created", "deleted")
    #             or _name in cls.__exclude_fields__
    #         ):
    #             continue
    #         has_default: bool = False
    #         try:
    #             _ = col.default
    #             has_default = True
    #         except AttributeError:
    #             has_default = False
    #         default: Any = ...
    #         if has_default is True:
    #             default = getattr(getattr(col, "default", None), "arg", None)
    #         t: Type | None = None
    #         if isinstance(col.type, DateTime):
    #             t = datetime
    #         elif isinstance(col.type, Date):
    #             t = date
    #         elif isinstance(col.type, Boolean):
    #             t = bool
    #         elif isinstance(col.type, Integer):
    #             t = int
    #         elif isinstance(col.type, Float):
    #             t = float
    #         elif isinstance(col.type, (String, Text)):
    #             t = str
    #         if t is None:
    #             continue
    #         _def[_name] = (t, default)
    #     return create_model("Out" + cls.__name__ + "Schema", **_def)
