import typing as t
from datetime import date

from pydantic import BaseModel, Field, model_validator

from arxivsearch.database.arxiv import ArxivPaperModelBase
from arxivsearch.database.helpers import get_categories
from arxivsearch.logger import get_logger

PossibleFacets = t.Literal["categories", "authors"]

CURRENT_YEAR = date.today().year
MINIMUM_YEAR = 1986  # SELECT create_date FROM arxiv_papers ORDER BY create_date ASC LIMIT 1;

logger = get_logger("arxiv_models")


class SubcategoryModel(BaseModel):
    id: str = Field(..., description="ID of the subcategory")
    name: str = Field(..., description="Human-friendly name of the subcategory")

    class Config:
        json_schema_extra = {
            "id": "cs.AI",
            "name": "Artificial Intelligence",
        }


class CategoryModel(BaseModel):
    id: str = Field(..., description="ID of the category")
    name: str = Field(..., description="Human-friendly name of the category")
    subcategories: t.List[SubcategoryModel] = Field(..., description="List of subcategories in this category")

    class Config:
        json_schema_extra = {
            "id": "cs",
            "name": "Computer Science",
            "subcategories": [
                {
                    "id": "cs.AI",
                    "name": "Artificial Intelligence",
                },
                {
                    "id": "cs.CV",
                    "name": "Computer Vision",
                },
            ],
        }


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


class Pagination(BaseModel):
    total_records: int = Field(..., description="Total number of results")
    total_pages: int = Field(..., description="Total number of pages")

    current_page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of results per page")

    class Config:
        json_schema_extra = {
            "total_records": 1000,
            "total_pages": 100,
            "current_page": 1,
            "size": 10,
        }


class SearchQuery(BaseModel):
    search: str = Field(..., description="Search term to query", min_length=1, max_length=100)

    author: str | None = Field(None, description="Author name to search for")
    subject: t.List[str] | None = Field([], description="Subject categories to search in")

    year_start: int = Field(
        MINIMUM_YEAR, ge=MINIMUM_YEAR, le=CURRENT_YEAR, description="Year range start for the search"
    )
    year_end: int = Field(CURRENT_YEAR, ge=MINIMUM_YEAR, le=CURRENT_YEAR, description="Year range end for the search")

    published: bool = Field(False, description="Only return papers that have been published (have a DOI)")

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

        # TODO: we shouldn't create this set every time, but rather cache it
        valid_categories = {
            subcat["id"] for cat in parsed_categories.values() for subcat in cat["subcategories"].values()
        }
        valid_categories.update(parsed_categories.keys())

        if not all([subject in valid_categories for subject in self.subject]):
            raise ValueError("Invalid subject categories provided")
        return self


class SearchResponse(BaseModel):
    pagination: Pagination = Field(..., description="Pagination information for the search results")
    time_to_search: int = Field(..., description="Time taken to search in ms")

    papers: t.List[ArxivPaperModelBase] = Field(..., description="List of papers found in the search")

    available_facets: t.List[FacetByResult] = Field(..., description="Facets available for the search")

    found_per_year: t.Dict[int, int] = Field(..., description="Number of papers found per year")
