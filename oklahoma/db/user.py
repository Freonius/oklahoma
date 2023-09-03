from datetime import datetime
from typing import overload, Literal, Type, TypeVar
from sqlalchemy import (
    DateTime,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from .base import Base

T = TypeVar("T", bound=Base)


class User(Base):
    email: Mapped[str]
    password: Mapped[str]
    last_access: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=None,
        nullable=True,
    )

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        attr: str,
        many: Literal[False],
        raise_on_none: Literal[True],
    ) -> T:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        attr: str,
        many: Literal[False],
        raise_on_none: Literal[False],
    ) -> T | None:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        attr: str,
        many: Literal[True],
        raise_on_none: bool,
    ) -> list[T]:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        many: Literal[False],
        raise_on_none: Literal[True],
    ) -> T:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        many: Literal[False],
        raise_on_none: Literal[False],
    ) -> T | None:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        many: Literal[True],
        raise_on_none: bool,
    ) -> list[T]:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        attr: str,
        many: Literal[False],
    ) -> T | None:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        attr: str,
        many: Literal[True],
    ) -> list[T]:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        many: Literal[False],
    ) -> T | None:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        many: Literal[True],
    ) -> list[T]:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
        *,
        attr: str,
    ) -> list[T]:
        ...

    @overload
    def get_joined_table(
        self,
        table: Type[T],
    ) -> list[T]:
        ...

    def get_joined_table(
        self,
        table: Type[T],
        *,
        attr: str = "user_id",
        many: bool = False,
        raise_on_none: bool = False,
    ) -> T | list[T] | None:
        pass
