import datetime
import time
import typing as t
from multiprocessing import Manager, Process

import typesense
from prepare_typesense import unix_time_millis

YEAR_2020 = datetime.datetime(2020, 1, 1, 0, 0, 0)

queries = {
    "abstract simple": lambda: {
        "q": "quantum",
        "query_by": "abstract",
        "sort_by": "_text_match:desc",
        "limit_hits": 1000,
    },
    "abstract": lambda: {
        "q": "machine learning models",
        "query_by": "abstract",
        "sort_by": "_text_match:desc",
        "limit_hits": 1000,
    },
    "abstract simple AND year+": lambda: {
        "q": "quantum",
        "query_by": "abstract",
        "filter_by": f"update_date:>{unix_time_millis(YEAR_2020)}",
        "sort_by": "_text_match:desc",
        "limit_hits": 1000,
    },
    "abstract AND year+": lambda: {
        "q": "machine learning models",
        "query_by": "abstract",
        "filter_by": f"update_date:>{unix_time_millis(YEAR_2020)}",
        "sort_by": "_text_match:desc",
        "limit_hits": 1000,
    },
    "(submitter OR category) AND year-": lambda: {
        "q": "John",
        "query_by": "submitter",
        "filter_by": f"categories:cs.AI && update_date:<{unix_time_millis(YEAR_2020)}",
        "sort_by": "_text_match:desc",
        "limit_hits": 1000,
    },
    "(abstract OR title) AND category": lambda: {
        "q": "artificial neural network",
        "query_by": "abstract,title",
        "filter_by": f"(title:`deep`) && categories:cs.AI",
        "sort_by": "_text_match:desc",
        "limit_hits": 1000,
    },
}


class TaskProcess(Process):
    ts: typesense.Client

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
        self.ts = typesense.Client(
            {
                "api_key": "test",
                "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
            }
        )

    def run(self):
        i = 0
        start = time.perf_counter_ns()
        while i < self.n:
            self.ts.collections[self.collection].documents.search(self.query())
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
            print(f"{benchmark(1000, query, concurrency): 5f}", end=", ")
        print()
