from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models import Base

_engine = None
_SessionMaker = None

async def init_db(database_url: str):
    global _engine, _SessionMaker
    _engine = create_async_engine(database_url, echo=False)
    _SessionMaker = async_sessionmaker(_engine, expire_on_commit=False)

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def get_session() -> AsyncSession:
    if _SessionMaker is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionMaker()
