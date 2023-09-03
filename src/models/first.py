from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from oklahoma.db import Base
from oklahoma import environ


class First(Base):
    message: Mapped[str]
    with_default: Mapped[str | None] = mapped_column(
        String,
        default=None,
        nullable=True,
    )


route = First.generate_crud_routes(before_insert=lambda x: environ.log.info(x))
