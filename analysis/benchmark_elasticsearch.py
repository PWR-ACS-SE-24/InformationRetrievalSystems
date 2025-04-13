import datetime
import time
import typing as t
from multiprocessing import Manager, Process

from elasticsearch import Elasticsearch

YEAR_2020 = datetime.datetime(2020, 1, 1, 0, 0, 0)

queries = {
    "abstract simple": lambda: {"match": {"abstract": {"query": "quantum"}}},
    "abstract": lambda: {"match": {"abstract": {"query": "machine learning models"}}},
    "abstract simple AND year+": lambda: {
        "bool": {
            "must": [{"match": {"abstract": {"query": "quantum"}}}],
            "filter": [
                {"range": {"update_date": {"gte": YEAR_2020.strftime("%Y-%m-%d")}}}
            ],
        },
    },
    "abstract AND year+": lambda: {
        "bool": {
            "must": [{"match": {"abstract": {"query": "machine learning models"}}}],
            "filter": [
                {"range": {"update_date": {"gte": YEAR_2020.strftime("%Y-%m-%d")}}}
            ],
        },
    },
    "(submitter OR category) AND year-": lambda: {
        "bool": {
            "should": [
                {"match": {"submitter": {"query": "John"}}},
                {"match": {"categories": "cs.AI"}},
            ],
            "filter": [
                {"range": {"update_date": {"lte": YEAR_2020.strftime("%Y-%m-%d")}}}
            ],
        }
    },
    "(abstract OR title) AND category": lambda: {
        "bool": {
            "should": [
                {"match": {"abstract": {"query": "artificial neural network"}}},
                {"match": {"title": {"query": "artificial neural network"}}},
            ],
            "filter": [{"match": {"categories": "cs.AI"}}],
        }
    },
}


class TaskProcess(Process):
    es: Elasticsearch

    def __init__(
        self,
        n: int,
        collection: str,
        query: t.Callable[[str], dict],
        return_dict: dict,
    ):
        super().__init__()

        self.return_dict = return_dict
        self.n = n
        self.collection = collection
        self.query = query
        self.es = Elasticsearch("http://localhost:9200")

    def run(self):
        i = 0
        start = time.perf_counter_ns()
        while i < self.n:
            self.es.search(
                index=self.collection,
                query=self.query(),
                request_cache=False,
                sort={"_score": {"order": "desc"}},
            )
            i += 1

        self.return_dict[self.ident] = time.perf_counter_ns() - start


if __name__ == "__main__":

    def benchmark(n: int, query: dict, concurrency: int):
        manager = Manager()
        return_dict = manager.dict()

        tasks = [
            TaskProcess(n, "arxiv", query, return_dict) for _ in range(concurrency)
        ]
        [task.start() for task in tasks]
        [task.join() for task in tasks]

        return sum(return_dict.values()) / len(return_dict) / 1e9

    for name, query in queries.items():
        print(name, end=": ")
        for concurrency in [1, 5, 10, 20, 50]:
            print(f"{benchmark(100, query, concurrency): 5f}", end=", ")
        print()
