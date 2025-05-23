from fastapi.routing import APIRouter

from arxivsearch.logger import get_logger

health_router = APIRouter(prefix="/health", tags=["main"])
logger = get_logger("health")


@health_router.get("")
def main():
    return {"status": "ok"}
