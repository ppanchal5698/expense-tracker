"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    print("App starting...")
    yield
    print("App shutting down...")
    from app.database.connection import engine
    await engine.dispose()


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Expense Management API",
        "version": settings.API_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/health/db")
async def health_check_db():
    """Database connectivity check endpoint."""
    from sqlalchemy import text
    from app.database.connection import async_session

    try:
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

