from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from src.config import Config

# Create an async engine
async_engine = create_async_engine(
    url=Config.DATABASE_URL, echo=True  # Add `echo=True` for debugging SQL queries, remove in production
)

# Initialize the database (create tables)
async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Dependency to get an async session
async def get_session() -> AsyncSession:
    # Configure the sessionmaker
    async_session_factory = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create and yield a session
    async with async_session_factory() as session:
        yield session
