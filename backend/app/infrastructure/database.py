from functools import lru_cache
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session

from .config import Settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)


def get_db_session() -> Iterator[Session]:
    settings = Settings()
    with Session(get_engine(settings.database_url)) as session:
        yield session
