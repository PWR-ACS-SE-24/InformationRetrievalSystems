import typing as t

from fastapi import APIRouter

from arxivsearch.database.helpers import get_categories
from arxivsearch.logger import get_logger
from arxivsearch.routes.models import CategoryModel, SubcategoryModel

logger = get_logger("categories")
categories_router = APIRouter(prefix="/categories", tags=["categories"])


def _normalize_category(d: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    # i want to make checking types as painless as possible, thus making categories a weird datastructure
    return CategoryModel(
        id=d["id"], name=d["name"], subcategories=[SubcategoryModel(**subcat) for subcat in d["subcategories"].values()]
    )


#         {
#         "id": d["id"],
#         "name": d["name"],
#         "subcategories": list(d["subcategories"].values()),
#     }


@categories_router.get("", response_model=t.List[CategoryModel])
async def get_human_categories():
    logger.debug("Getting all categories")

    return [_normalize_category({"id": k, **v}) for k, v in get_categories().items()]
