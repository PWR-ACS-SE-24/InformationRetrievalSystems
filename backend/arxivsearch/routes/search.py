import json
import typing as t
from datetime import date

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field, model_validator
from sqlmodel import col, select

import arxivsearch.config as config
from arxivsearch.database import SessionDep
from arxivsearch.database.arxiv import ArxivPaperModel, ArxivPaperModelBase
from arxivsearch.elastic import ElasticDep
from arxivsearch.logger import get_logger

logger = get_logger("search")
search_router = APIRouter(prefix="/search", tags=["search"])

CURRENT_YEAR = date.today().year

PossibleFacets = t.Literal["categories", "authors"]


# this is kinda overkill, cos we send "field" value multiple times
# TODO: think of something better than this
class FacetBy(BaseModel):
    field: PossibleFacets = Field(..., description="Field to facet by")
    value: str = Field(..., description="Value to facet by", min_length=1, max_length=100)

    class Config:
        schema_extra = {
            "field": "categories",
            "value": "cs.AI",
        }


class FacetByResult(FacetBy):
    count: int = Field(..., description="Count of papers in this facet")

    class Config:
        schema_extra = {
            "example": {
                "field": "categories",
                "value": "cs.AI",
                "count": 2137,
            }
        }


class SearchQuery(BaseModel):
    search: str = Field(..., description="Search term to query", min_length=1, max_length=100)

    author: str | None = Field(None, description="Author name to search for")
    subject: str | None = Field(None, description="Subject category to search in")

    year_start: int = Field(2000, ge=2000, le=CURRENT_YEAR, description="Year range start for the search")
    year_end: int = Field(CURRENT_YEAR, ge=2000, le=CURRENT_YEAR, description="Year range end for the search")

    # how the fuck are we going to achieve this?
    open_access: bool = Field(True, description="Only return open access papers")

    facet_by: t.List[FacetBy] | None = Field([], description="Set facets to search in", max_length=10)

    @model_validator(mode="after")
    def check_years(self) -> t.Self:
        if self.year_end < self.year_start:
            raise ValueError("Year start should be less or equal to year end")
        return self


class SearchResponse(BaseModel):
    time_to_search: int = Field(..., description="Time taken to search in ms")
    total: int = Field(..., description="Total number of results")

    papers: t.List[ArxivPaperModelBase] = Field(..., description="List of papers found in the search")

    available_facets: t.List[FacetByResult] = Field(..., description="Facets available for the search")


@search_router.post("", response_model=SearchResponse)
def search(
    search_query: SearchQuery,
    session: SessionDep,
    elastic: ElasticDep,
    skip: t.Annotated[int, Query(ge=0, description="Skip n first results")] = 0,
    limit: t.Annotated[int, Query(ge=1, description="Limit results")] = 30,
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
    }
    aggs = {
        "categories-agg": {
            "terms": {
                "field": "categories",
                "size": 10,
            }
        },
        "submitter-agg": {
            "terms": {
                "field": "submitter",
                "size": 10,
            }
        },
    }

    # execute query
    result = elastic.search(
        index="arxiv", sort={"_score": {"order": "desc"}}, query=query, size=limit, from_=skip, aggs=aggs
    )

    # parse result
    time_to_search = result["took"]
    hits = result["hits"]["hits"]
    total_hits = result["hits"]["total"]["value"]

    if config.DEBUG:
        logger.debug(f"Query: {json.dumps(query)}")
        logger.debug(f"Result: {json.dumps(result.body)}")
    logger.debug(f"Got {len(hits)} hits")
    logger.debug(f"Got {total_hits} total hits")
    logger.debug(f"Took {time_to_search} ms to search")

    ids = [hit["_id"] for hit in hits]

    logger.debug(f"Ids: {ids}")

    # get papers from database
    with session.exec(select(ArxivPaperModel).where(col(ArxivPaperModel.arxiv_id).in_(ids))) as results:
        papers = list(results.all())

    logger.debug(f"Got {len(papers)} papers from database")

    paper_map = dict.fromkeys(ids)
    for paper in papers:
        paper_map[paper.arxiv_id] = paper

    categories_facets = result["aggregations"]["categories-agg"]["buckets"]
    submitter_facets = result["aggregations"]["submitter-agg"]["buckets"]

    all_facets = [
        *[
            FacetByResult(field="categories", value=facet["key"], count=facet["doc_count"])
            for facet in categories_facets
        ],
        *[FacetByResult(field="authors", value=facet["key"], count=facet["doc_count"]) for facet in submitter_facets],
    ]

    # prepare response
    return SearchResponse(
        time_to_search=time_to_search, total=total_hits, papers=paper_map.values(), available_facets=all_facets
    )
