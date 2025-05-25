import json
import typing as t
from datetime import date

from fastapi import APIRouter, Query
from sqlmodel import col, select

import arxivsearch.config as config
from arxivsearch.database import SessionDep
from arxivsearch.database.arxiv import ArxivPaperModel
from arxivsearch.elastic import ElasticDep
from arxivsearch.logger import get_logger
from arxivsearch.routes.models import (
    FacetByResult,
    Pagination,
    SearchQuery,
    SearchResponse,
)

logger = get_logger("search")
search_router = APIRouter(prefix="/search", tags=["search"])


@search_router.post("", response_model=SearchResponse)
def search(
    search_query: SearchQuery,
    session: SessionDep,
    elastic: ElasticDep,
    page: t.Annotated[int, Query(ge=0, description="Skip n first results")] = 0,
    perpage: t.Annotated[int, Query(ge=1, lte=30, description="Limit results")] = 30,
):

    date_start = date(search_query.year_start, 1, 1)
    date_end = date(search_query.year_end + 1, 1, 1)

    # prepare query
    additional_musts = []

    if search_query.author:
        additional_musts.append(
            {"multi_match": {"query": search_query.author, "fields": ["authors"]}},
        )

    if search_query.published:
        additional_musts.append({"exists": {"field": "refid"}})

    if search_query.subject:
        cats = []
        for search_subject, subcategories in search_query.subject.items():
            if not subcategories:
                continue

            cats.extend([f"{search_subject}.{subcat}" for subcat in subcategories])

        # match any of the subcategories
        additional_musts.append(
            {
                "terms": {
                    "categories": cats,
                }
            }
        )

    for facet in search_query.facet_by:
        additional_musts.append({"match": {facet.field: {"query": facet.value}}})

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
        "authors-agg": {
            "terms": {
                "field": "authors",
                "size": 10,
            }
        },
        "year-agg": {
            "date_range": {
                "field": "update_date",
                "format": "yyyy",
                "ranges": [{"from": i, "to": i + 1} for i in range(search_query.year_start, search_query.year_end + 1)],
            }
        },
    }

    # execute query
    result = elastic.search(
        index="arxiv",
        sort={"_score": {"order": "desc"}},
        query=query,
        size=perpage,
        from_=perpage * page,
        aggs=aggs,
        track_total_hits=True,
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
    author_facets = result["aggregations"]["authors-agg"]["buckets"]
    year_facets = result["aggregations"]["year-agg"]["buckets"]

    all_facets = [
        *[
            FacetByResult(field="categories", value=facet["key"], count=facet["doc_count"])
            for facet in categories_facets
        ],
        *[FacetByResult(field="authors", value=facet["key"], count=facet["doc_count"]) for facet in author_facets],
    ]

    years = {
        str(facet["from_as_string"]): facet["doc_count"] for facet in year_facets if facet["from_as_string"] is not None
    }

    pagination = Pagination(
        total_records=total_hits,
        total_pages=(total_hits // perpage) + (total_hits % perpage > 0),
        current_page=page,
        size=len(hits),
    )

    # prepare response
    return SearchResponse(
        pagination=pagination,
        time_to_search=time_to_search,
        papers=paper_map.values(),
        available_facets=all_facets,
        found_per_year=years,
    )
