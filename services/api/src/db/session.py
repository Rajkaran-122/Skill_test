"""
Async database session management using SQLAlchemy + asyncpg.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
import src.db.models  # Ensure models are loaded for metadata

_engine = None
_session_factory = None


async def init_db(database_url: str) -> None:
    """Initialize the async database engine and session factory."""
    global _engine, _session_factory

    if database_url.startswith("sqlite"):
        _engine = create_async_engine(
            database_url,
            echo=False,
        )
        # Create tables for sqlite local mock
        async with _engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    else:
        _engine = create_async_engine(
            database_url,
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=False,
        )

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def close_db() -> None:
    """Close the database engine."""
    global _engine
    if _engine:
        await _engine.dispose()


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async database session."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized")

    async with _session_factory() as session:
        try:
            yield session
            # We explicitly do NOT commit here unconditionally.
            # Commits should be handled by the route or a transactional middleware.
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
