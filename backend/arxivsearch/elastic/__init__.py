import typing as t

from elasticsearch import Elasticsearch
from fastapi import Depends

import arxivsearch.config as config

_elastic_client: t.Optional[Elasticsearch] = None


# TODO: replace with elasticsearch-dsl
def setup_elastic() -> Elasticsearch:
    global _elastic_client
    if _elastic_client is None:
        _elastic_client = Elasticsearch(
            hosts=config.ELASTIC_URL,
            timeout=30,
            max_retries=10,
            retry_on_timeout=True,
        )
    return _elastic_client


def get_elastic_client():
    global _elastic_client
    if _elastic_client is None:
        setup_elastic()

    yield _elastic_client


ElasticDep = t.Annotated[Elasticsearch, Depends(get_elastic_client)]
