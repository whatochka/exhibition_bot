from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    image_path: Mapped[str | None] = mapped_column(nullable=True)
    voice_path: Mapped[str | None] = mapped_column(nullable=True)
    items = relationship("Item", back_populates="zone", cascade="all, delete")
