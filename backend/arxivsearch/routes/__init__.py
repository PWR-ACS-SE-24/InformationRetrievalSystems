from arxivsearch.routes.categories import categories_router
from arxivsearch.routes.health import health_router

routers = [health_router, categories_router]

__all__ = ["routes"]
