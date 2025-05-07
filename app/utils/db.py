from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.base import Base
import os

DB_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DB_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_pool():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # ← создаем таблицы


def get_session():
    return SessionLocal()
