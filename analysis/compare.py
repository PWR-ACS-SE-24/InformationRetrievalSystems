from base64 import standard_b64encode as b64encode

from benchmark_elasticsearch import queries as es_queries
from benchmark_typesense import queries as ts_queries
from elasticsearch import Elasticsearch
from typesense.client import Client

DEFAULT_COLLECTION = "arxiv"


ts = Client(
    {
        "api_key": "test",
        "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
    }
)

es = Elasticsearch("http://localhost:9200", request_timeout=30)


def compare_query(query_name: str):
    ts_query = ts_queries[query_name]()
    ts_results = ts.collections[DEFAULT_COLLECTION].documents.search({
                                                                     **ts_query})

    es_query = es_queries[query_name]()
    es_results = es.search(index=DEFAULT_COLLECTION, query=es_query)

    print(ts_results["found"], es_results["hits"]["total"]["value"])


for key in ts_queries.keys():
    print(key, end=": ")
    compare_query(key)
