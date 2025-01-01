from sqlmodel import create_engine, text,SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config
from sqlmodel.ext.asyncio.session import AsyncSession


engine = AsyncEngine(
    create_engine(
    url = Config.DATABASE_URL,
    echo = True
))

async def init_db():
    async with engine.begin() as conn:
        from src.books.models import Book

        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    pass

