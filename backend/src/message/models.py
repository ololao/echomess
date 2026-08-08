from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.users import User


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(primary_key=True)
    data: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    user: Mapped["User"] = relationship()
