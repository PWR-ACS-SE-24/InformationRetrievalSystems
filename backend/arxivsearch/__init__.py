from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import arxivsearch.config as config
from arxivsearch.logger import setup_logger

logger = setup_logger()

from arxivsearch.database import setup_database
from arxivsearch.elastic import setup_elastic
from arxivsearch.routes import routers


def create_app() -> FastAPI:

    logger.info("Hello from arxivsearch, starting up...")
    app = FastAPI(redirect_slashes=False, debug=config.DEBUG)

    app.state.engine_database = setup_database()
    app.state.engine_elasticsearch = setup_elastic()
    
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for router in routers:
        logger.debug(f"Registering router: /api{router.prefix}")
        app.include_router(router, prefix="/api")

    return app


app = create_app()
