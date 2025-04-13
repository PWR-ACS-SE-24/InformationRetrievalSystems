import json
import time
from datetime import datetime
from itertools import islice

import requests
import typesense
from tqdm import tqdm

_epoch = datetime.fromtimestamp(0)


def unix_time_millis(dt):
    return int((dt - _epoch).total_seconds() * 1000.0)


def batched(iterable, n, *, strict=False):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError("batched(): incomplete batch")
        yield batch


def fix_line(line: str) -> dict:
    parsed = json.loads(line)
    parsed["categories"] = parsed["categories"].split(" ")
    parsed["title"] = parsed["title"].replace("\n", " ")
    parsed["abstract"] = parsed["abstract"].replace("\n", " ")

    return parsed


def get_index_size() -> dict:
    request = requests.get(
        "http://localhost:8108/metrics.json", headers={"X-TYPESENSE-API-KEY": "test"}
    )
    return {i: float(j) for i, j in request.json().items() if i.startswith("typesense")}


def _fix_line_date(line: str) -> dict:
    parsed = fix_line(line)
    epoch = datetime.strptime(parsed["update_date"], "%Y-%m-%d")
    parsed["update_date"] = unix_time_millis(epoch)
    return parsed


if __name__ == "__main__":
    ts = typesense.Client(
        {
            "api_key": "test",
            "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
            "connection_timeout_seconds": 30,
        }
    )

    schema = {
        "fields": [
            {"name": "id", "type": "string", "index": False, "facet": False},
            {"name": "submitter", "type": "string", "index": True, "facet": True},
            # ciekawe czy to by miało sens
            {"name": "authors", "type": "string", "index": False, "facet": False},
            {
                "name": "title",
                "type": "string",
                "index": True,
                "facet": False,
                "store": False,
                "stem": True,
            },
            {"name": "comments", "type": "string", "index": False, "facet": False},
            {"name": "journal-ref", "type": "string", "index": False, "facet": False},
            {"name": "doi", "type": "string", "index": False, "facet": False},
            {
                "name": "abstract",
                "type": "string",
                "index": True,
                "facet": False,
                "store": False,
                "stem": True,
            },
            {"name": "categories", "type": "string[]", "index": True, "facet": True},
            {"name": "versions.*", "type": "auto", "index": False, "facet": False},
            {"name": "update_date", "type": "int64", "index": True},
        ],
    }

    try:
        ts.collections["arxiv"].delete()
    except Exception as e:
        pass
    ts.collections.create({"name": "arxiv", **schema})

    with open("arxiv-metadata-oai-snapshot.json", "r") as file:
        elapsed = []
        usage = [get_index_size()]

        length = sum(1 for _ in file)
        file.seek(0)

        start = time.perf_counter()
        batch_size = (length // 25) + 1

        for chunk in tqdm(batched(file, batch_size)):
            ts.collections["arxiv"].documents.import_(map(_fix_line_date, chunk))

            usage.append(get_index_size())
            elapsed.append(time.perf_counter() - start)

    with open("typesense_stats.json", "w") as file:
        json.dump({"time": elapsed, "usage": usage}, file, indent=1)
