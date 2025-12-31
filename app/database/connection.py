"""Database connection and engine configuration."""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings


engine = create_async_engine(
    settings.database_url_async,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_MAX,
    max_overflow=10,
    connect_args={
        "server_settings": {"jit": "off"},
        "statement_cache_size": 0,
    },
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

