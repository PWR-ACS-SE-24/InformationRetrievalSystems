import typing as t

from fastapi import Depends
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, SQLModel

import arxivsearch.config as config
from arxivsearch.database.arxiv import ArxivCategoriesModel, ArxivPaperModel

_engine: t.Optional[Engine] = None


def setup_database() -> Engine:
    global _engine
    if _engine:
        return _engine

    _engine = create_engine(config.DATABASE_URL)
    SQLModel.metadata.create_all(_engine)

    return _engine


def get_database_session():
    global _engine

    with Session(_engine) as session:
        yield session


models = [ArxivCategoriesModel, ArxivPaperModel]

__all__ = ["ArxivPaperModel", "ArxivCategoriesModel", "models", "setup_database", "get_database_session"]
SessionDep = t.Annotated[Session, Depends(get_database_session)]
