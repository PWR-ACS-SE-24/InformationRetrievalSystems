import json
import typing as t
from datetime import date

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field, model_validator
from sqlmodel import col, select

import arxivsearch.config as config
from arxivsearch.database import SessionDep
from arxivsearch.database.arxiv import ArxivPaperModel
from arxivsearch.elastic import ElasticDep
from arxivsearch.logger import get_logger

logger = get_logger("search")
categories_router = APIRouter(prefix=["/search"], tags=["search"])

CURRENT_YEAR = date.today().year


class FacetBy(BaseModel):
    pass


class SearchQuery(BaseModel):
    search: str = Field(..., description="Search term to query", min_length=1)

    author: str | None = Field(None, description="Author name to search for")
    subject: str | None = Field(None, description="Subject category to search in")

    year_start: int = Field(..., ge=2000, le=CURRENT_YEAR, description="Year range start for the search")
    year_end: int = Field(..., ge=2000, le=CURRENT_YEAR, description="Year range end for the search")

    # how the fuck are we going to achieve this?
    open_access: bool = Field(True, description="Only return open access papers")

    facet_by: t.List[FacetBy] | None = Field(..., description="Set facets to search in")

    @model_validator(mode="after")
    def check_years(self) -> t.Self:
        if self.year_end < self.year_start:
            raise ValueError("Year start should be less or equal to year end")
        return self


class SearchResponse(BaseModel):
    pass


@categories_router.post("")
def search(
    search_query: SearchQuery,
    session: SessionDep,
    elastic: ElasticDep,
    skip: t.Annotated[int, Query(default=0, ge=0, description="Skip n first results")],
    limit: t.Annotated[int, Query(default=30, ge=1, description="Limit results")],
):

    date_start = date(search_query.year_start, 1, 1)
    date_end = date(search_query.year_end + 1, 1, 1)

    # prepare query
    additional_musts = []
    if search_query.author:
        additional_musts.append(
            {"multi_match": {"query": search_query.author, "fields": ["authors", "submitter"]}},
        )

    if search_query.subject:
        additional_musts.append({"match": {"category": {"query": search_query.subject}}})

    query = {
        "bool": {
            "must": [
                {"multi_match": {"query": search_query.search, "fields": ["abstract", "title"]}},
                *additional_musts,
            ],
            "filter": [
                {
                    "range": {
                        "update_date": {"gte": date_start.strftime("%Y-%m-%d"), "lt": date_end.strftime("%Y-%m-%d")}
                    }
                }
            ],
        },
        "aggs": {
            "categories-agg": {
                "terms": {
                    "field": "categories.keyword",
                    "size": 10,
                }
            },
            "submitter-agg": {
                "terms": {
                    "field": "submitter",
                    "size": 10,
                }
            },
        },
    }

    # execute query
    result = elastic.search(
        index="arxiv", source=False, sort={"_score": {"order": "desc"}}, query=query, size=limit, from_=skip
    )

    # parse result
    time_to_search = result["took"]
    hits = result["hits"]["hits"]

    if config.DEBUG:
        logger.debug(f"Query: {json.dumps(result, indent=2)}")
    logger.debug(f"Got {len(hits)} hits")
    logger.debug(f"Got {result['hits']['total']['value']} total hits")
    logger.debug(f"Got {time_to_search} ms to search")

    ids = [hit["_id"] for hit in hits]

    # get papers from database
    with session.exec(select(ArxivPaperModel).where(col(ArxivPaperModel.arxiv_id).in_(ids))) as results:
        papers = list(results.all())

    logger.debug(f"Got {len(papers)} papers from database")

    # when downloading data from postgres, the order is not guaranteed
    # TODO: order is achieved in O(n^2)
    papers.sort(key=lambda x: ids.index(x.id))

    # prepare response
    return {}
