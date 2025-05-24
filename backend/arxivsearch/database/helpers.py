import typing as t
from collections import defaultdict

from sqlalchemy import Engine
from sqlmodel import Session, select

from arxivsearch.database.arxiv import ArxivCategoriesModel
from arxivsearch.logger import get_logger

logger = get_logger("helpers")

parsed_categories: t.Optional[t.List[t.Dict[str, t.Any]]] = None


def get_categories() -> t.List[t.Dict[str, t.Any]]:
    if parsed_categories is None:
        raise ValueError("Categories have not been preloaded. Call preload_categories first.")

    return parsed_categories


def preload_categories(engine: Engine):
    global parsed_categories

    with Session(engine) as session:
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

    categories = defaultdict(lambda: {"name": "", "subcategories": []})

    for category in found_categories:
        if category.subcategory:
            categories[category.category]["subcategories"].append(
                {"id": f"{category.category}.{category.subcategory}", "name": category.name}
            )
        else:
            categories[category.category]["name"] = category.name

    parsed_categories = [{"id": k, **v} for k, v in categories.items()]
