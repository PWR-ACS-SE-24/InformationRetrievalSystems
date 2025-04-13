from collections import Counter
import pandas as pd
from elasticsearch import Elasticsearch
import typesense
import datetime
from prepare_typesense import unix_time_millis

results = {
    "typesense": [],
    "elasticsearch": [],
}

YEAR_2020 = datetime.datetime(2020, 1, 1, 0, 0, 0)


def get_all_ids_elasticsearch(query):
    es = Elasticsearch("http://localhost:9200")
    response = es.search(
        index="arxiv",
        query=query,
        scroll='5m',
        size=1000
    )

    scroll_id = response['_scroll_id']
    hits = response['hits']['hits']
    all_ids = [hit['_id'] for hit in hits]

    while len(hits):
        response = es.scroll(scroll_id=scroll_id, scroll='5m')
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']
        all_ids.extend([hit['_id'] for hit in hits])

    return all_ids


def get_all_ids_typesense(query):
    ts = typesense.Client(
        {
            "api_key": "test",
            "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
        }
    )

    all_ids = []
    page = 1
    page_size = 250
    query["per_page"] = page_size

    while True:
        query["page"] = page

        results = ts.collections["arxiv"].documents.search(query)

        hits = results.get("hits", [])
        if not hits:
            break

        ids = [hit["document"]["id"] for hit in hits]
        all_ids.extend(ids)
        page += 1

    return all_ids


# -------- 1
results["elasticsearch"].append(get_all_ids_elasticsearch(
    {"match_phrase": {"abstract": {"query": "nanostructures"}}}))
results["typesense"].append(get_all_ids_typesense({
    "q": "nanostructures",
    "query_by": "abstract",
    "sort_by": "_text_match:desc",
}))

# -------- 2
results["elasticsearch"].append(get_all_ids_elasticsearch(
    {"match_phrase": {"abstract": {"query": "machine learning models"}}}))
results["typesense"].append(get_all_ids_typesense({
    "q": "machine learning models",
    "query_by": "abstract",
    "sort_by": "_text_match:desc",
}))

# -------- 3
results["elasticsearch"].append(get_all_ids_elasticsearch({
    "bool": {
        "must": [{"match_phrase": {"abstract": {"query": "nanostructures"}}}],
        "filter": [
            {"range": {"update_date": {
                "gte": YEAR_2020.strftime("%Y-%m-%d")}}}
        ],
    },
}))
results["typesense"].append(get_all_ids_typesense({
    "q": "nanostructures",
    "query_by": "abstract",
    "filter_by": f"update_date:>{unix_time_millis(YEAR_2020)}",
    "sort_by": "_text_match:desc",
}))

# -------- 4
results["elasticsearch"].append(get_all_ids_elasticsearch({
    "bool": {
        "must": [{"match_phrase": {"abstract": {"query": "machine learning models"}}}],
        "filter": [
            {"range": {"update_date": {
                "gte": YEAR_2020.strftime("%Y-%m-%d")}}}
        ],
    },
}))
results["typesense"].append(get_all_ids_typesense({
    "q": "machine learning models",
    "query_by": "abstract",
    "filter_by": f"update_date:>{unix_time_millis(YEAR_2020)}",
    "sort_by": "_text_match:desc",
}))

# # -------- 5
# results["elasticsearch"].append(get_all_ids_elasticsearch({
#     "bool": {
#         "must": [
#             {"match": {"submitter": {"query": "John"}}},
#             {"match": {"categories": "cs.AI"}},
#         ],
#         "filter": [
#             {"range": {"update_date": {
#                 "lte": YEAR_2020.strftime("%Y-%m-%d")}}}
#         ],
#     }
# }))
# results["typesense"].append(get_all_ids_typesense({
#     "q": "John",
#     "query_by": "submitter",
#     "filter_by": f"categories:=cs.AI && update_date:<{unix_time_millis(YEAR_2020)}",
#     "sort_by": "_text_match:desc",
# }))

# # -------- 6
# results["elasticsearch"].append(get_all_ids_elasticsearch({
#     "bool": {
#         "should": [
#             {"match_phrase": {"abstract": {"query": "artificial neural network"}}},
#             {"match_phrase": {"title": {"query": "artificial neural network"}}},
#         ],
#         "filter": [{"match": {"categories": "cs.AI"}}],
#     }
# }))
# results["typesense"].append(get_all_ids_typesense({
#     "q": "artificial neural network",
#     "query_by": "abstract,title",
#     "filter_by": f"categories:=cs.AI",
#     "sort_by": "_text_match:desc",
# }))

N = len(results["elasticsearch"])

print("Number of hits for each query:")

for engine in results:
    print(f"Results for {engine}:")
    for query in range(N):
        print(f"#{query}: {len(results[engine][query])} hits")

relevant_answers = [
    {a for a, c in Counter(
        a for engine in results for a in results[engine][query]).items() if c >= 2}
    for query in range(N)
]

print("\n")
print("Metrics for each engine:")

papers_count = 2700231

for engine in results:
    accuracy = []
    precision = []
    recall = []
    f1score = []
    mcc = []

    for query in range(N):
        retrieved = set(results[engine][query])
        relevant = relevant_answers[query]
        TP = len(retrieved & relevant)
        FP = len(retrieved-relevant)
        FN = len(relevant-retrieved)
        TN = papers_count-len(retrieved | relevant)
        accuracy.append((TP + TN) / papers_count)
        precision.append(TP / (TP + FP) if TP + FP > 0 else 0)
        recall.append(TP / (TP + FN))
        f1score.append(2 * TP / (2 * TP + FP + FN))
        mcc.append((TP * TN - FP * FN) / ((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN)) ** 0.5 if
                   (TP + FP) * (TP + FN) * (TN + FP) * (TN + FN) > 0 else 0)

    print(f"Results for {engine}:")
    print(f"  Accuracy:  {sum(accuracy) / len(accuracy):.3%} {accuracy}")
    print(f"  Precision: {sum(precision) / len(precision):.3%} {precision}")
    print(f"  Recall:    {sum(recall) / len(recall):.3%} {recall}")
    print(f"  F1-score:  {sum(f1score) / len(f1score):.3%} {f1score}")
    print(f"  MCC:       {sum(mcc) / len(mcc):.3%} {mcc}")


print("\n")
print("Correlation between engines:")


def corr(a: list[int], b: list[int]) -> float:
    common = set(a) & set(b)
    a = [e for e in a if e in common]
    b = [e for e in b if e in common]
    bi = pd.Series([a.index(e) for e in b])
    ai = pd.Series(list(range(len(a))))
    return (float(ai.corr(bi, method="pearson")) + 1) / 2


pairs = [
    ("elasticsearch", "typesense"),
]
for e1, e2 in pairs:
    print(f"{e1} vs {e2}:")
    corrs = [corr(results[e1][query], results[e2][query])
             for query in range(N)]
    for query in range(N):
        print(f"  #{query}: {corrs[query]:.3%}")
    print(f" avg: {sum(corrs) / len(corrs):.3%} {corrs}")
