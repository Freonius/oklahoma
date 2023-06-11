from sqlalchemy.orm import Mapped
from oklahoma.db import Base


class First(Base):
    message: Mapped[str]
