from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from vitalis.storage.models import Base


def build_database(database_url: str):
    engine_options = {}
    if database_url.endswith(":memory:"):
        from sqlalchemy.pool import StaticPool

        engine_options.update(
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    engine = create_async_engine(database_url, echo=False, **engine_options)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return engine, session_factory


async def initialize_database(engine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def session_dependency(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
