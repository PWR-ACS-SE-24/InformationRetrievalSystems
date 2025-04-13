import json
import time

from elasticsearch import Elasticsearch, helpers
from prepare_typesense import batched, fix_line
from tqdm import tqdm

index_mapping = {
    "properties": {
        "id": {"type": "keyword"},
        "submitter": {"type": "text"},
        "authors": {"type": "text"},
        "title": {"type": "text"},
        "comments": {"type": "text"},
        "journal-ref": {"type": "text"},
        "doi": {"type": "keyword"},
        # in elastic every field is an array
        "categories": {"type": "keyword"},
        "abstract": {"type": "text"},
        "update_date": {"type": "date", "format": "yyyy-MM-dd"},
    }
}

index_settings = {
    "index": {"max_result_window": 1_000_000},
}


def fix_lines(a): return map(fix_line, a)


def get_index_stats(client: Elasticsearch, index: str) -> int:
    index_stats = client.indices.stats(index=index)
    if index_stats and "indices" in index_stats:
        return index_stats["indices"][index]["total"]["store"]["size_in_bytes"]
    else:
        return -1


def get_fields(client: Elasticsearch, filename: str, indexname: str):
    def action_mapper(f): return {
        "_id": f["id"], "_index": indexname, "_source": f}

    elapsed = []
    usage = [get_index_stats(client, indexname)]

    with open(filename, "r") as file:
        length = sum(1 for _ in file)

        file.seek(0)

        start = time.perf_counter()

        for chunk in tqdm(batched(file, (length // 25) + 1)):
            helpers.bulk(client, list(map(action_mapper, fix_lines(chunk))))

            usage.append(get_index_stats(client, indexname))
            elapsed.append(time.perf_counter() - start)

    return elapsed, usage


if __name__ == "__main__":
    client = Elasticsearch("http://localhost:9200")

    if client.indices.exists(index="arxiv"):
        client.indices.delete(index="arxiv")

    client.indices.create(
        index="arxiv", mappings=index_mapping, settings=index_settings
    )
    stats = get_fields(client, "arxiv-metadata-oai-snapshot.json", "arxiv")

    with open("elastic_stats.json", "w") as file:
        json.dump({"time": stats[0], "usage": stats[1]}, file, indent=1)
