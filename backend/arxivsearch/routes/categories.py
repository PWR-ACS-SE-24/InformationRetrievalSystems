from fastapi import APIRouter
from sqlmodel import select

from arxivsearch.database import SessionDep
from arxivsearch.database.arxiv import ArxivCategoriesModel
from arxivsearch.logger import get_logger

logger = get_logger("categories")
categories_router = APIRouter(prefix="/categories", tags=["categories"])


@categories_router.get("")
async def get_human_categories(session: SessionDep):
    logger.debug("Getting all categories")

    with session.exec(select(ArxivCategoriesModel)) as result:
        categories = result.all()

    logger.debug(f"Got {len(categories)} categories")
    return {k.category: k.human_name for k in categories}
