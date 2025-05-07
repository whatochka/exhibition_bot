# models/item.py

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    photo = Column(String, nullable=True)
    voice = Column(String, nullable=True)

    zone = relationship("Zone", back_populates="items")
