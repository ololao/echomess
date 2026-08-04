from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Message(Base):
    __tablename__ = "messages"
    data: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime())
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
