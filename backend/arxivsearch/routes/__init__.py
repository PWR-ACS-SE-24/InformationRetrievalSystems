from arxivsearch.routes.categories import categories_router
from arxivsearch.routes.health import health_router
from arxivsearch.routes.search import search_router

routers = [health_router, categories_router, search_router]

__all__ = ["routes"]
