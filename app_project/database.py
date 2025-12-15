from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app_project.config import settings

engine = create_async_engine(url=settings.DATABASE_URL, pool_pre_ping=True)

session = async_sessionmaker(bind=engine)

@asynccontextmanager
async def session_context():
    async with session() as session_db:
        yield session_db

async def get_session():
    async with session_context() as local_session:
        yield local_session


class Base(DeclarativeBase):
    pass
