import typing as t
from collections import defaultdict

from sqlmodel import Session, select

from arxivsearch.database.arxiv import ArxivCategoriesModel
from arxivsearch.logger import get_logger

logger = get_logger("helpers")

parsed_categories: t.Optional[t.Dict[str, t.Any]] = None


def get_categories() -> t.Dict[str, t.Any]:
    if parsed_categories is None:
        logger.debug("Categories not preloaded, loading now...")
        preload_categories()

    return parsed_categories


def preload_categories():
    global parsed_categories

    if parsed_categories is not None:
        logger.debug("Categories already preloaded, skipping.")
        return

    import arxivsearch.database

    with Session(arxivsearch.database._engine) as session:
        logger.debug("Preloading categories...")
        with session.exec(select(ArxivCategoriesModel)) as result:
            found_categories = result.all()

        logger.debug(f"Found {len(found_categories)} categories in the database.")

    #    id: "cs",
    #    name: "Computer Science",
    #    subcategories: [
    #      { id: "cs.AI", name: "Artificial Intelligence" },
    #      { id: "cs.AR", name: "Hardware Architecture" },
    #     ...

    parsed_categories = defaultdict(lambda: {"name": "", "subcategories": {}})

    for category in found_categories:
        if category.subcategory:
            parsed_categories[category.category]["subcategories"][category.subcategory] = {
                "id": f"{category.category}.{category.subcategory}",
                "name": category.name,
            }
        else:
            parsed_categories[category.category]["name"] = category.name
