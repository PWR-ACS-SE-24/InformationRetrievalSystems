from fastapi import APIRouter

from arxivsearch.database.helpers import get_categories
from arxivsearch.logger import get_logger

logger = get_logger("categories")
categories_router = APIRouter(prefix="/categories", tags=["categories"])


@categories_router.get("")
async def get_human_categories():
    logger.debug("Getting all categories")

    return get_categories()
