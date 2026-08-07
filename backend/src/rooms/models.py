from sqlalchemy import Computed, String
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from src.database import Base


class Rooms(Base):
    __tablename__ = "rooms"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    tsv: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed(
        """
        setweight(to_tsvector('english', coalesce(name, '')), 'A')
        ||
        setweight(to_tsvector('russian', coalesce(name, '')), 'A')
        """,
            persisted=True,
        ),
    )
