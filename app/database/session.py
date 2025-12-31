"""Database session dependency for FastAPI."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import async_session


async def get_db() -> AsyncSession:
    """FastAPI dependency for database sessions."""
    async with async_session() as session:
        yield session

