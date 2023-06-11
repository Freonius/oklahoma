from sqlalchemy.orm import Mapped
from oklahoma.db import Base


class Second(Base):
    message: Mapped[str]
