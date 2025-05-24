import typing as t
from datetime import date

from pydantic import BaseModel, Field, model_validator

from arxivsearch.database.arxiv import ArxivPaperModelBase
from arxivsearch.database.helpers import get_categories
from arxivsearch.logger import get_logger

PossibleFacets = t.Literal["categories", "authors"]

CURRENT_YEAR = date.today().year

logger = get_logger("search_query")


# this is kinda overkill, cos we send "field" value multiple times
# TODO: think of something better than this
class FacetBy(BaseModel):
    field: PossibleFacets = Field(..., description="Field to facet by")
    value: str = Field(..., description="Value to facet by", min_length=1, max_length=100)

    class Config:
        json_schema_extra = {
            "field": "categories",
            "value": "cs.AI",
        }


class FacetByResult(FacetBy):
    count: int = Field(..., description="Count of papers in this facet")

    class Config:
        json_schema_extra = {
            "field": "categories",
            "value": "cs.AI",
            "count": 2137,
        }


class SearchQuery(BaseModel):
    search: str = Field(..., description="Search term to query", min_length=1, max_length=100)

    author: str | None = Field(None, description="Author name to search for")
    subject: t.Dict[str, t.List[str]] | None = Field({}, description="Subject categories to search in")

    year_start: int = Field(2000, ge=2000, le=CURRENT_YEAR, description="Year range start for the search")
    year_end: int = Field(CURRENT_YEAR, ge=2000, le=CURRENT_YEAR, description="Year range end for the search")

    published: bool = Field(False, description="Only return open access papers")

    facet_by: t.List[FacetBy] | None = Field([], description="Set facets to search in", max_length=10)

    @model_validator(mode="after")
    def check_years(self) -> t.Self:
        if self.year_end < self.year_start:
            raise ValueError("Year start should be less or equal to year end")
        return self

    @model_validator(mode="after")
    def check_subject(self) -> t.Self:
        if self.subject is None:
            return self

        parsed_categories = get_categories()

        if not all([k in parsed_categories for k in self.subject.keys()]):
            raise ValueError("Invalid subject categories provided")

        for cat, subcats in self.subject.items():
            logger.debug(f"Checking subcategories: {cat}")
            if not all([subcat in parsed_categories[cat]["subcategories"] for subcat in subcats]):
                raise ValueError(f"Invalid subject subcategories provided, offending category: {cat}")

        return self


class SearchResponse(BaseModel):
    time_to_search: int = Field(..., description="Time taken to search in ms")
    total: int = Field(..., description="Total number of results")

    papers: t.List[ArxivPaperModelBase] = Field(..., description="List of papers found in the search")

    available_facets: t.List[FacetByResult] = Field(..., description="Facets available for the search")
