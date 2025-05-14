import typing as t
from datetime import datetime

from sqlalchemy import Column, String
from sqlmodel import ARRAY, Field, SQLModel


class ArxivPaperModelBase(SQLModel):

    # ID for arxiv purposes
    arxiv_id: str = Field(index=True, nullable=False)
    doi: str | None = Field(index=True, nullable=True)

    authors: t.List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String())))

    submitter: str = Field(nullable=False)

    title: str = Field(nullable=False)
    abstract: str = Field(nullable=False)

    # this can be none for some reason?
    journal_ref: str | None = Field(default=None)

    categories: t.List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String())))

    # useless
    comments: str | None = Field(default=None)
    update_date: datetime = Field(nullable=False)

    class Config:
        arbitrary_types_allowed = True


class ArxivPaperModel(ArxivPaperModelBase, table=True):
    __tablename__ = "arxiv_papers"

    # ID for database purposes
    id: int | None = Field(default=None, primary_key=True)


class ArxivCategoriesModel(SQLModel, table=True):
    __tablename__ = "arxiv_categories"

    id: int | None = Field(default=None, primary_key=True)

    category: str = Field(nullable=False)
    human_name: str = Field(nullable=False)
