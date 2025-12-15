from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app_project.config import settings

engine = create_async_engine(url=settings.DATABASE_URL, pool_pre_ping=True)

session = async_sessionmaker(bind=engine)


async def get_session():
    async with session() as local_session:
        yield local_session


class Base(DeclarativeBase):
    pass
