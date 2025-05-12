from sqlalchemy import Integer, String, Text, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Subzone(Base):
    __tablename__ = "subzones"

    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    photo = Column(String, nullable=True)
    voice = Column(String, nullable=True)

    zone = relationship("Zone", back_populates="subzones")
    items = relationship("Item", back_populates="subzone", cascade="all, delete")
