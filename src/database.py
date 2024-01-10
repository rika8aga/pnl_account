from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings


engine = create_async_engine(url=settings.db_url, echo=True, poolclass=NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session_maker() as session:
#         yield session
class Base(DeclarativeBase):
    repr_columns: list[str] = []

    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join([f"{col}={getattr(self, col)!r}" for col in self.repr_columns])})'
